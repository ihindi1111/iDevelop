"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from idevelop import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name = 'home'),

    # Google oAuth routes
    path('accounts/', include('allauth.urls')),
    
    # Authentication routes

    ## Replacing Google AUTH
    path('register-action', views.register_action, name = 'register-action'),
    path('login-action', views.login_action, name = 'login-action'),
    ## Replacing Google AUTH
    path('home/', views.home_action, name = 'home_action'),
    path('', auth_views.logout_then_login, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('credits/', views.credits, name='credits'),
    path('materials/', views.materials, name='materials'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    
    path('permit-edits/<int:user_id>/', views.permit_edits, name='permit-edits'),
    path('prevent-edits/<int:user_id>/', views.prevent_edits, name='prevent-edits'),

    path('settings/', views.settings, name='settings'),
    path('collab/<int:box_id>/', views.collab, name='collab'),
    path('post-welcome/', views.post_welcome, name='post-welcome'),
    path('lesson1/', views.lesson1, name='lesson1'),
    path('lesson2/', views.lesson2, name='lesson2'),
    path('lesson3/', views.lesson3, name='lesson3'),
    path('submit_answer_1/<int:lesson>/<int:question>/', views.submit_answer_1, name='submit_answer_1'),
    path('submit_answer_2/<int:lesson>/<int:question>/', views.submit_answer_2, name='submit_answer_2'),
    path('submit_answer_3/<int:lesson>/<int:question>/', views.submit_answer_3, name='submit_answer_3'),
    path('students/', views.students_list, name='students'),
    path('send-friend-request/<int:id>/', views.send_friend_request, name='send_friend_request'),
    path('cancel-friend-request/<int:friend_request_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('accept-friend-request/<int:friend_request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)