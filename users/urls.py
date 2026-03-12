from django.urls import path 
from .views  import *

urlpatterns = [
    path('' ,login , name='login'),
    path('home/' ,home , name='home'),
    path('department/' ,department , name='department'),
    path('products/', products, name='product'),
    path('logout/' ,logout , name='logout'),
    path('ajax-form/', ajax_page, name='ajax_page'),
    path('add-student/', add_student, name='add_student'),
    path('add-student/<int:id>/', add_student, name='update_student'),
    path('list-student/', list_student, name='list_student'),
    path('list-bill/', list_bill, name='list_bill'),
    path('add-bill/', add_bill, name='add_bill'),
     path('ajax-get-students/', ajax_get_students, name='ajax_get_students'),
     path('get-product-price/', get_product_price, name='get_product_price'),
    path('add-bill/<int:id>/', add_bill, name='update_bill'),
    path('change-password/', change_password, name='change_password'),
    path('department-sales/', dept_sales, name='dept_sales'),
    path('students-sales/', student_sales, name='student_sales'),
    path('product-sales/', product_sales, name='product_sales'),
    path('export-department-sales/<str:type>/', export_dept_sales, name='export_dept_sales'), # type: ignore

]
