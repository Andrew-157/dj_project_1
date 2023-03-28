from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import View
from .forms import CustomUserForm, ChangeCustomUserForm, PublishArticleForm
from .models import CustomUser, Article, Reaction


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
                                  'admin@gmail.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="articles/password/password_reset.html", context={"password_reset_form": password_reset_form})


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
    article = Article.objects.filter(pk=article_id).first()
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
            return redirect('articles:index')
    form = PublishArticleForm(instance=article)
    return render(request, 'articles/update_article.html', {'form': form, 'article': article})


def public_article(request, article_id):
    current_user = request.user
    user_reaction_message = None
    likes = 0
    dislikes = 0
    article = Article.objects.select_related('author').\
        prefetch_related('tags').\
        filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/nonexistent.html')
    if current_user.is_authenticated:
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
    return render(request, 'articles/public_article.html', {'article': article,
                                                            'user_reaction_message': user_reaction_message,
                                                            'likes': likes,
                                                            'dislikes': dislikes})


def like_article(request, article_id):
    current_user = request.user
    article = Article.objects.filter(pk=article_id).first()
    # when this view redirects you back to the public page of the article
    # this does not count as article was read one more time
    # so article.times_read becomes bigger only
    # when you hit public-article url
    article.times_read -= 1
    article.save()
    if not article:
        return render(request, 'articles/nonexistent.html')
    # here login_required decorator is not applied
    # because we want user to return to the public page of the article
    # with message that they need to be authenticated to leave a reaction
    if not current_user.is_authenticated:
        messages.info(request, 'To leave a reaction, please, sign in')
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
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
    article = Article.objects.filter(pk=article_id).first()
    article.times_read -= 1
    article.save()
    if not article:
        return render(request, 'articles/nonexistent.html')
    if not current_user.is_authenticated:
        messages.info(request, 'To leave a reaction, please, sign in')
        return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
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
