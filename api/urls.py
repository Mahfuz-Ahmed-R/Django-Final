from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('product', views.ProductViewSet)
router.register('order', views.OrderViewSet)
router.register('order-item', views.OrderItemViewSet)
router.register('wishlist', views.WishListViewSet)
router.register('review', views.ReviewViewSet)
router.register('shipping-address', views.ShippingAddressViewSet)
router.register('inventory', views.InventoryViewSet)
router.register('category', views.CategoryViewSet)
router.register('sub-category', views.SubCategoryViewSet)
router.register('size', views.SizeViewSet)
router.register('color', views.ColorViewSet)
router.register('myorders', views.MyOrdersViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/register/', views.UserRegistrationAPIView.as_view(), name='register'),
    path('active/<uid64>/<token>/', views.activate, name='activate'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('order-delete/<int:pk>/<int:id>/', views.OrderItemDeleteView.as_view(), name='order-delete'),
    path('my-order-delete/<int:pk>/<int:id>/', views.MyOrderDeleteView.as_view(), name='my-order-delete'),
    path('customer/<int:user_id>/', views.CustomerDetail.as_view(), name='customer-detail'),
    path('order-details/<int:user_id>/<str:value>/', views.OrderDetail.as_view(), name='order-details'),
    path('category_view/', views.ProductByCategoryView.as_view(), name='category-slug'),
    path('get_inventory/<int:id>/', views.InvetoryGetView.as_view(), name='get_inventory'),
    path('product_by_price/<int:id>/', views.ProductByCategoryViewByPrice.as_view(), name='product_by_price'),
    path('user/edit_profile/', views.UserProfileUpdateView.as_view(), name='edit_profile'),
    path('user/change_password/', views.UserChangePasswordView.as_view(), name='change_password'),
]
