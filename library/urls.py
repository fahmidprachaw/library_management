from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('books/', views.BookListView.as_view(), name='all_books'),
    path('book/<int:pk>/', views.BookDetailsView.as_view(), name='book_detail'),
    path('diposite/', views.DepositeView.as_view(), name='deposite'),
    path('book/<int:pk>/borrow/', views.BorrowBookView.as_view(), name='borrow_book'),
    path('borrowed-book/', views.BorrowedBookView.as_view(), name='borrowed_book'),
    path('return-book/<int:pk>/', views.ReturnBookView.as_view(), name='return_book'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)