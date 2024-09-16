from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import FollowUserForm, SignUpForm, TicketForm
from itertools import chain
from django.db.models import Value, CharField
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, Ticket, UserFollows, User
from . import models
from django.contrib.auth import logout
from django.db.models import Q, Value, CharField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Value, CharField
from itertools import chain
from .forms import SignUpForm, TicketForm, ReviewForm, FollowUserForm
from .models import Ticket, Review, UserFollows, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import TicketForm
from .models import Ticket

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import UserFollows

@login_required
def unfollow_user(request, follow_id):
    follow = get_object_or_404(UserFollows, id=follow_id, user=request.user)
    if request.method == 'POST':
        follow.delete()
    return redirect('view_followed_users')

@login_required
def view_followed_users(request):
    followed_users = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)
    return render(request, 'reviews/followed_users.html', {'followed_users': followed_users, 'followers': followers})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'reviews/edit_ticket.html', {'form': form})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('posts')
    return render(request, 'reviews/delete_review.html', {'review': review})


def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('feed')  # Ou utilisez LOGIN_REDIRECT_URL
    else:
        form = AuthenticationForm()
    return render(request, 'reviews/login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'reviews/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('feed')
    else:
        form = AuthenticationForm()
    return render(request, 'reviews/login.html', {'form': form})


@login_required
def view_posts(request):
    tickets = Ticket.objects.filter(user=request.user).annotate(content_type=Value('TICKET', CharField()))
    reviews = Review.objects.filter(user=request.user).annotate(content_type=Value('REVIEW', CharField()))
    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, 'reviews/posts.html', {'posts': posts})

@login_required
def create_review_for_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('feed')
    else:
        form = ReviewForm()
    return render(request, 'reviews/create_review_for_ticket.html', {'form': form, 'ticket': ticket})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/edit_review.html', {'form': form})


@login_required
def create_review(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('feed')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()
    return render(request, 'reviews/create_review.html', {'ticket_form': ticket_form, 'review_form': review_form})


@login_required
def feed(request):
    reviews = get_users_viewable_reviews(request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    tickets = get_users_viewable_tickets(request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request, 'reviews/feed.html', context={'posts': posts})

def get_users_viewable_reviews(user):
    followed_users = user.following.all().values_list('followed_user', flat=True)
    reviews = Review.objects.filter(
        Q(user__in=followed_users) | Q(user=user)
    )
    return reviews


def get_users_viewable_tickets(user):
    followed_users = user.following.all().values_list('followed_user', flat=True)
    tickets = Ticket.objects.filter(
        Q(user__in=followed_users) | Q(user=user)
    )
    return tickets

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('feed')
    else:
        form = TicketForm()
    return render(request, 'reviews/create_ticket.html', {'form': form})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('feed')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'reviews/edit_ticket.html', {'form': form})


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    if request.method == 'POST':
        ticket.delete()
        return redirect('feed')
    return render(request, 'reviews/delete_ticket.html', {'ticket': ticket})

@login_required
def follow_user(request):
    if request.method == 'POST':
        form = FollowUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                followed_user = User.objects.get(username=username)
                if followed_user != request.user:
                    UserFollows.objects.get_or_create(user=request.user, followed_user=followed_user)
                    messages.success(request, f"Vous suivez maintenant {username}.")
                else:
                    messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
            except User.DoesNotExist:
                messages.error(request, "Utilisateur non trouvé.")
            return redirect('follow_user')
    else:
        form = FollowUserForm()
    return render(request, 'reviews/follow_user.html', {'form': form})

@login_required
def view_followed_users(request):
    followed_users = request.user.following.all()
    followers = request.user.followed_by.all()
    return render(request, 'reviews/followed_users.html', {'followed_users': followed_users, 'followers': followers})

