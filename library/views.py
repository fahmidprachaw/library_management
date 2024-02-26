from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from .forms import RegistretionForm
from django.views.generic import FormView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from .models import Book, BorrowedBook, UserProfile
from .forms import ReviewForm, DepositeForm
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

# Create your views here.
# def Profile(request):
#     return render(request, 'library/profile.html')


def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()

class RegistrationView(FormView):
    template_name = 'library/registration.html'
    form_class = RegistretionForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = 'library/login.html'

    def get_success_url(self) -> str:
        return reverse_lazy('profile')
    

class UserLogoutView(LogoutView):
    def get_success_url(self):
        return reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return HttpResponseRedirect(self.get_success_url())


   
# class ProfileView(View):
#     template_name = 'library/profile.html'

#     def get()
    
class BookListView(ListView):
    model = Book
    template_name = 'library/all_books.html'
    context_object_name = 'books'



class BookDetailsView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.review_set.all()
        context['form'] = ReviewForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = self.get_object()
            review.save()
            messages.success(request, 'Your review has been submitted.')
            return redirect('book_detail', pk=self.kwargs['pk'])
        else:
            return self.form_invalid(form)
        

class DepositeView(LoginRequiredMixin, FormView):
    template_name = 'library/deposite.html'
    form_class = DepositeForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        print(amount)
        user_profile = self.request.user.userprofile
        print(user_profile)
        user_profile.balance += amount
        print(user_profile.balance)
        user_profile.save()
        messages.success(self.request, f'You have successfully deposited ${amount}. Your current balance is ${user_profile.balance}.')
        send_transaction_email(self.request.user, amount, 'Deposite Message', 'library/deposite_mail.html')
        return super().form_valid(form)
    
class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'library/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        # return self.request.user.userprofile
        user_profile = getattr(self.request.user, 'userprofile', None)
        if user_profile:
            return user_profile
        else:
            # If UserProfile does not exist, create one
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            return user_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance'] = self.request.user.userprofile.balance
        return context
    


class BorrowBookView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        book_pk = kwargs.get('pk')
        book = Book.objects.get(pk=book_pk)
        borrowing_price = book.price
        print(borrowing_price)
        user_profile = request.user.userprofile
        print(user_profile.balance)
        if user_profile.balance >= borrowing_price:
            user_profile.balance -= borrowing_price
            user_profile.save()
            BorrowedBook.objects.create(user=request.user, book=book)
            messages.success(request, f'You have successfully borrowed "{book.title}".')
            send_transaction_email(self.request.user, 0, 'Borrowing Book', 'library/borrow_mail.html')
        else:
            messages.error(request, f'Insufficient balance to borrow "{book.title}".')
        return redirect('borrowed_book')
    


class BorrowedBookView(LoginRequiredMixin, ListView):
    model = BorrowedBook
    template_name = 'library/borrowed_book_list.html'
    context_object_name = 'borrowed_books'

    def get_queryset(self):
        return BorrowedBook.objects.filter(user=self.request.user)


class ReturnBookView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        borrowed_book_pk = kwargs.get('pk')
        borrowed_book = BorrowedBook.objects.get(pk=borrowed_book_pk)
        book = borrowed_book.book
        borrowing_price = book.price
        user_profile = request.user.userprofile
        user_profile.balance += borrowing_price
        user_profile.save()
        borrowed_book.delete()
        messages.success(request, f'You have successfully returned the book.')
        return redirect('borrowed_book')

