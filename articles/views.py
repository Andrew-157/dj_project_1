from django.db.models import Sum
from django.db.models.query_utils import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import BadHeaderError, send_mail
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import View
from taggit.models import Tag
from .forms import SocialMediaForm, CustomUserForm, ChangeCustomUserForm, PublishArticleForm, CommentArticleForm
from .models import CustomUser, Article, Reaction, Comment, Subscription, SocialMedia, UserReadings


def password_reset_request(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = CustomUser.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = 'articles/password/password_reset_email.txt'
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",
                        "site_name": "Articlee",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http"
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email,
                                  'admin1@gmail.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="articles/password/password_reset.html", context={"password_reset_form": password_reset_form})


class AddSocialMediaLink(View):
    form_class = SocialMediaForm
    template_name = 'articles/add_social_media.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(
                request, 'You successfully added new link to your social media')
            return redirect('articles:personal-page')
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required()
def delete_social_media(request, social_media_id):
    current_user = request.user
    social_media = SocialMedia.objects.\
        select_related('user').\
        filter(pk=social_media_id).first()
    if not social_media:
        return render(request, 'articles/nonexistent.html')
    if social_media.user != current_user:
        return render(request, 'articles/not_yours.html')
    social_media.delete()
    return redirect('articles:personal-page')


class RegisterUser(View):
    form_class = CustomUserForm
    template_name = 'articles/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to the Articlee')
            return redirect('articles:index')

        return render(request, self.template_name, {'form': form})


class LoginUser(View):
    form_class = AuthenticationForm
    template_name = 'articles/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(
                    request, f"Welcome back to the Articlee")
                return redirect('articles:index')
        return render(request, self.template_name, {'form': form})


def logout_request(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('articles:index')


class ChangeUser(View):
    form_class = ChangeCustomUserForm
    template_name = 'articles/change_user.html'

    def get(self, request):
        current_user = request.user
        form = self.form_class(instance=current_user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        current_user = request.user
        form = self.form_class(
            request.POST, request.FILES, instance=current_user)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f'Your account was successfully changed')
            return redirect('articles:index')
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PublishArticle(View):
    form_class = PublishArticleForm
    template_name = 'articles/publish_article.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, 'You successfully published new article')
            return redirect('articles:index')
        return render(request, 'articles/publish_article.html', {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required()
def update_article(request, article_id):
    current_user = request.user
    article = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/nonexistent.html')
    if article.author != current_user:
        return render(request, 'articles/not_yours.html')
    if request.method == 'POST':
        form = PublishArticleForm(request.POST,
                                  request.FILES,
                                  instance=article)
        if form.is_valid():
            obj = form.save(commit=False)
            form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.success(
                request, 'You successfully updated your article')
            return redirect('articles:personal-page')
    form = PublishArticleForm(instance=article)
    return render(request, 'articles/update_article.html', {'form': form, 'article': article})


@login_required()
def delete_article(request, article_id):
    current_user = request.user
    article = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/nonexistent.html')
    if article.author != current_user:
        return render(request, 'articles/not_yours.html')
    article.delete()
    messages.success(request, 'Your article was successfully deleted')
    return redirect('articles:personal-page')


def public_article(request, article_id):
    current_user = request.user
    user_reaction_message = None
    likes = 0
    dislikes = 0
    comments = None
    article = Article.objects.select_related('author').\
        prefetch_related('tags').\
        filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/nonexistent.html')
    if current_user.is_authenticated:
        user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                    Q(article=article)).first()
        if not user_readings:
            user_readings = UserReadings(
                user=current_user,
                article=article,
                times_read=1
            )
            user_readings.save()
        else:
            user_readings.times_read += 1
            user_readings.save()
        article.times_read += 1
        article.save()
        user_reaction = Reaction.objects.filter(
            Q(article=article)
            &
            Q(reaction_owner=current_user)
        ).first()
        if user_reaction:
            if user_reaction.value == -1:
                user_reaction_message = 'You disliked this article'
            if user_reaction.value == 1:
                user_reaction_message = 'You liked this article'
    article_reactions = Reaction.objects.filter(article=article).all()
    if article_reactions:
        likes = article_reactions.filter(value=1).count()
        dislikes = article_reactions.filter(value=-1).count()
    article_comments = Comment.objects.filter(
        article=article).select_related('commentator').all()
    if article_comments:
        comments = article_comments
    return render(request, 'articles/public_article.html', {'article': article,
                                                            'user_reaction_message': user_reaction_message,
                                                            'likes': likes,
                                                            'dislikes': dislikes,
                                                            'comments': comments})


def like_article(request, article_id):
    current_user = request.user
    if not current_user.is_authenticated:
        # here login_required decorator is not applied
        # because we want user to return to the public page of the article
        # with message that they need to be authenticated to leave a reaction
        messages.info(
            request, 'To leave a reaction, please, become an authenticated user')
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/nonexistent.html')
    user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                Q(article=article)).first()
    if not user_readings:
        # this if statement ensures that view works properly as
        # we check if user read an article and does not try to hit
        # url for likes directly
        messages.warning(
            request, "Do not try to leave like without reading an article")
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
    else:
        # when this view redirects you back to the public page of the article
        # this does not count as user read
        user_readings.times_read -= 1
        user_readings.save()
    # when this view redirects you back to the public page of the article
    # this does not count as article was read one more time
    # so article.times_read only increases
    # when you hit public-article url
    article.times_read -= 1
    article.save()
    reaction = Reaction.objects.filter(
        Q(article=article)
        &
        Q(reaction_owner=current_user)
    ).first()
    if not reaction:
        reaction = Reaction(
            value=1, reaction_owner=current_user, article=article)
        reaction.save()
    else:
        if reaction.value == -1:
            reaction.value = 1
            reaction.save()
        elif reaction.value == 1:
            reaction.delete()

    return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))


def dislike_article(request, article_id):
    # this view is basically the same as like_article
    # but with the opposite values
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(request, 'To leave a reaction, please, sign in')
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/nonexistent.html')
    user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                Q(article=article)).first()
    if not user_readings:
        messages.warning(
            request, "Do not try to leave dislike without reading an article")
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
    else:
        user_readings.times_read -= 1
        user_readings.save()
    article.times_read -= 1
    article.save()
    reaction = Reaction.objects.filter(
        Q(article=article)
        &
        Q(reaction_owner=current_user)
    ).first()
    if not reaction:
        reaction = Reaction(
            value=-1, reaction_owner=current_user, article=article)
        reaction.save()
    else:
        if reaction.value == 1:
            reaction.value = -1
            reaction.save()
        elif reaction.value == -1:
            reaction.delete()

    return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))


def comment_article(request, article_id):
    current_user = request.user
    if not current_user.is_authenticated:
        # here login_required decorator is not applied
        # because we want user to return to the public page of the article
        # with message that they need to be authenticated to leave a comment
        messages.info(
            request, 'To leave a comment, please, become an authenticated user')
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
    article = Article.objects.filter(pk=article_id).\
        select_related('author').first()
    if not article:
        return render(request, 'articles/nonexistent.html')
    user_readings = UserReadings.objects.filter(Q(user=current_user) &
                                                Q(article=article)).first()
    if not user_readings:
        messages.warning(
            request, "Do not try to leave comment without reading an article")
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
    if request.method == 'POST':
        article.times_read -= 1
        article.save()
        user_readings.times_read -= 1
        user_readings.save()
        form = CommentArticleForm(request.POST)
        if form.is_valid():
            form.instance.commentator = current_user
            form.instance.article = article
            if article.author == current_user:
                form.instance.is_author = True
            form.save()
            messages.success(
                request, 'You successfully left a comment on this article')
            return HttpResponseRedirect(reverse('articles:public-article', args=(article_id, )))
    form = CommentArticleForm()
    return render(request, 'articles/comment_article.html', {'form': form, 'article': article})


def find_articles_through_tag(request, tag):
    tag_object = Tag.objects.filter(name=tag).first()
    if not tag_object:
        return render(request, 'articles/nonexistent.html')
    articles = Article.objects.prefetch_related('tags').\
        filter(tags=tag_object).order_by('-times_read').all()
    number_of_articles = len(articles)
    if number_of_articles < 0:
        message_to_display = f'No articles were found with this tag #{tag_object}'
    if number_of_articles == 1:
        message_to_display = f'One article was found with this tag #{tag_object}'
    if number_of_articles > 1:
        message_to_display = f'{number_of_articles} articles were found with this tag #{tag_object}'
    return render(request, 'articles/public_articles.html', {'message_to_display': message_to_display,
                                                             'articles': articles})


def author_page(request, author):
    current_user = request.user
    subscription_status = 'Subscribe'
    total_readings = None
    is_owner = False
    author_object = CustomUser.objects.filter(username=author).first()
    if not author_object:
        return render(request, 'articles/nonexistent.html')
    if current_user == author_object:
        is_owner = True
    articles = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        order_by('-pub_date').\
        filter(author=author_object).all()
    if articles:
        total_readings = sum(articles.values_list('times_read', flat=True))
    if current_user.is_authenticated:
        subscription = Subscription.objects.filter(
            Q(subscriber=current_user) &
            Q(subscribe_to=author_object)
        ).first()
        # this subscription status is shown
        # as button, so if user is subscribed
        # they see unsubscribe button and vice versa
        if subscription:
            subscription_status = 'Unsubscribe'
        else:
            subscription_status = 'Subscribe'
    subscribers = Subscription.objects.filter(
        subscribe_to=author_object).count()
    social_media = SocialMedia.objects.filter(user=author_object).all()
    return render(request, 'articles/author_page.html', {'author': author_object,
                                                         'articles': articles,
                                                         'total_readings': total_readings,
                                                         'number_of_articles': len(articles),
                                                         'subscribers': subscribers,
                                                         'subscription_status': subscription_status,
                                                         'is_owner': is_owner,
                                                         'social_media': social_media})


@login_required()
def personal_page(request):
    current_user = request.user
    total_readings = None
    articles = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        order_by('-pub_date').\
        filter(author=current_user).\
        all()
    if articles:
        total_readings = sum(articles.values_list('times_read', flat=True))
    number_of_articles = len(articles)
    subscribers = Subscription.objects.filter(
        subscribe_to=current_user).count()
    social_media = SocialMedia.objects.\
        filter(user=current_user).all()

    return render(request, 'articles/personal_page.html', {'current_user': current_user,
                                                           'articles': articles,
                                                           'total_readings': total_readings,
                                                           'number_of_articles': number_of_articles,
                                                           'subscribers': subscribers,
                                                           'social_media': social_media})


def subscribe_request(request, author):
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(
            request, 'To subscribe you need to be an authenticated user')
        return HttpResponseRedirect(reverse('articles:author-page', args=(author,)))
    author_object = CustomUser.objects.filter(username=author).first()
    if not author_object:
        return render(request, 'articles/nonexistent.html')
    if current_user == author_object:
        messages.info(request, 'You cannot subscribe to yourself')
        return HttpResponseRedirect(reverse('articles:author-page', args=(author,)))
    subscription = Subscription.objects.filter(
        Q(subscriber=current_user) &
        Q(subscribe_to=author_object)
    ).first()
    if not subscription:
        subscription = Subscription(
            subscriber=current_user,
            subscribe_to=author_object
        )
        subscription.save()
        messages.success(request, 'You successfully subscribed to this author')
        return HttpResponseRedirect(reverse('articles:author-page', args=(author, )))
    else:
        subscription.delete()
        messages.success(
            request, 'You successfully unsubscribed from this author')
        return HttpResponseRedirect(reverse('articles:author-page', args=(author, )))


def search_articles(request):
    search_string = request.POST['search_string']
    if not search_string:
        return render(request, 'articles/nonexistent.html')
    if len(search_string) == 1 and search_string[0] == '#':
        return render(request, 'articles/nonexistent.html')
    if search_string[0] == '#':
        tag = search_string[1:]
        return HttpResponseRedirect(reverse('articles:tag-article', args=(tag, )))
    articles = Article.objects.\
        select_related('author').\
        prefetch_related('tags').\
        filter(Q(title__icontains=search_string) |
               Q(author__username__icontains=search_string)).\
        order_by('-times_read').\
        all()
    number_of_articles = len(articles)
    if number_of_articles == 0:
        message_to_display = f"No articles were found that contain ---{search_string}--- \
            in author's name or title"
    elif number_of_articles == 1:
        message_to_display = f"1 article was found that contains ---{search_string}--- \
            in author's name or title"
    else:
        message_to_display = f"{number_of_articles} articles were found that contain ---{search_string}---\
            in author's name or title"

    return render(request, 'articles/public_articles.html', {'message_to_display': message_to_display,
                                                             'articles': articles})


def recommend_articles(request):
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(
            request, "Become an authenticated user, so we can recommend you articles")
        return redirect('articles:index')
