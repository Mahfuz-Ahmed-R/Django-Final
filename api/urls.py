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
    path('order-delete/<int:pk>/', views.OrderItemDeleteView.as_view(), name='order-delete'),
    path('my-order-delete/<int:pk>/', views.MyOrderDeleteView.as_view(), name='my-order-delete'),
    path('customer/<int:user_id>/', views.CustomerDetail.as_view(), name='customer-detail'),
    path('order-details/<int:user_id>/', views.OrderDetail.as_view(), name='order-details'),
    path('category_view/<slug:category_slug>/<slug:subcategory_slug>/', views.ProductByCategoryView.as_view(), name='category-subcategory-slug'),

    # path('api/product/', views.ProdcutViewAPI.as_view(), name='product'),
    # path('api/product/<int:pk>/', views.ProductDetailAPI.as_view(), name='product-detail'),
    # path('api/color/', views.ColorViewAPI.as_view(), name='color'),
    # path('api/size/', views.SizeViewAPI.as_view(), name='color'),
    # path('api/category/', views.CategoryViewAPI.as_view(), name='category'),
    # path('api/sub-category/', views.SubCategoryViewAPI.as_view(), name='sub-category'),
    # path('api/inventory/', views.InventoryViewAPI.as_view(), name='inevntory'),
    # path('api/order/', views.OrderViewAPI.as_view(), name='order'),
    # path('api/order-item/', views.OrderItemViewAPI.as_view(), name='order-item'),
    # path('api/wishlist/', views.WishListViewAPI.as_view(), name='wishlist'),
    # path('api/review/<int:pk>/', views.ReviewViewAPI.as_view(), name='review'),
    # path('api/shipping-address/', views.ShippingAddressViewAPI.as_view(), name='shipping-address'),
]
