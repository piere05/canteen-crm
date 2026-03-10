from genericpath import exists
from itertools import product
from tkinter.tix import STATUS

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *

import os
from django.conf import settings


# Create your views here.


def login(request):

    if "user_id" in request.session:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = Users.objects.filter(username=username, password=password).first()

        if user:
            request.session['user_id'] = user.pk
            return redirect('home')
        else:
            messages.error(request, "Username or Password Incorrect")
            return redirect('login')

    return render(request, 'index.html')



def home(request):
         if "user_id" not in request.session:
            return redirect('login')

         return render(request ,'home.html')


def ajax_page(request):
    act = request.POST.get("act")
    id_val = request.POST.get("id")

    if act=='department' and request.method== "POST":
        if int(id_val)!=0:
            department_data = Department.objects.filter(id=id_val).first()
            context = {"act" : "department" , "department_data" :department_data }
        else:
            context = {"act" : "department"}
        return render(request ,'ajax-modal.html',context)
    
    if act=='product' and request.method== "POST":
        if int(id_val)!=0:
            product_data = Products.objects.filter(id=id_val).first()
            context = {"act" : "product" , "product_data" :product_data }
        else:
            context = {"act" : "product"}
        return render(request ,'ajax-modal.html',context)


    return render(request ,'ajax-modal.html')
     
     

def department(request):
         
         if "user_id" not in request.session:
            return redirect('login')
         if request.method=="POST":
              department_name = request.POST.get("dept_name")
              status = request.POST.get("status")
              MainId = request.POST.get("MainId")
              exists = Department.objects.filter(dept_name=department_name).exclude(id=MainId).exists()
              if exists :
                  messages.error(request,"Department Already Exists")
              else:
                if MainId and int(MainId) > 0:
                   Department.objects.filter(id=MainId).update(dept_name=department_name,status=status)
                   messages.success(request,"Department Updated Successfully")
                else: 
                    Department.objects.create(dept_name=department_name,status=status)
                    messages.success(request,"Department Created Successfully")
              return redirect('department')
         department_id = request.GET.get("id")
         act = request.GET.get("act")
         if act == "delete" and department_id:

             try:
                Department.objects.filter(id=department_id).delete()
                messages.success(request,"Department Deleted Successfully")
             except Exception:
                messages.error(request, "Could Able to Delete Try again once")
             return redirect('department')
         depaqrtments = Department.objects.all().order_by('-id')
         context = {"department_data" : depaqrtments}
         return render(request ,'department.html',context)




def products(request):
         if "user_id" not in request.session:
            return redirect('login')
         if request.method=="POST":
             product_name = request.POST.get("productname")
             price = request.POST.get("price")
             status = request.POST.get("status")
             UploadedImage = request.FILES.get('imagepath')
             print(UploadedImage)
             MainId = request.POST.get("MainId")
             exists = Products.objects.filter(productname =product_name).exclude(id=MainId).exists()
             select_pro = Products.objects.filter(id=MainId).first() 
             if exists:
                 messages.error(request,"Product Already Exists")
             else:
                 if int(MainId)==0:
                     Products.objects.create(productname=product_name,status=status,price=price,imagepath=UploadedImage)
                     messages.success(request,"Product Created Successfully")
                 else:
                    product = Products.objects.get(id=MainId)
                    if UploadedImage:
                        if product.imagepath and os.path.exists(product.imagepath.path):
                             os.remove(product.imagepath.path)
                             product.imagepath = UploadedImage

                    product.productname = product_name
                    product.status = status
                    product.price = price
                    product.save()
                    messages.success(request,"Product Updated Successfully")
             return redirect('product')
            
         product_ID = request.GET.get("id")
         act = request.GET.get("act")
         if act == "delete" and product_ID:
             select_pro = Products.objects.filter(id=product_ID).first() 
             try:
                if os.path.exists(select_pro.imagepath.path): # type: ignore
                    os.remove(select_pro.imagepath.path) # pyright: ignore[reportOptionalMemberAccess]
                select_pro.delete() # type: ignore
                messages.success(request,"Product Deleted Successfully")
             except Exception:
                messages.error(request, "Could Able to Delete Try again once")
             return redirect('product')
                     
         product_data = Products.objects.all().order_by("-id")
         context = {"product_data" :  product_data}
         return render(request ,'product.html' ,context)




def add_student(request,id=0):
    if request.method=="POST":
        studnetname = request.POST.get("name")
        studnetmobile = request.POST.get("mobile")
        studnetemail = request.POST.get("email")
        studnetstatus = request.POST.get("status")
        studnetaddress = request.POST.get("address")
        studnetdept= request.POST.get("dept_id")
        studnetid= request.POST.get("studnetid")
        check_ex = Students.objects.filter(mobile=studnetmobile).exclude(id=id).exists()
        if check_ex:
            messages.error(request,"Student Already exists")
            return redirect('list_student')
        else:
            if id==0:
                Students.objects.create(name=studnetname,mobile=studnetmobile,email=studnetemail,status=studnetstatus,department_id=studnetdept,address=studnetaddress)
                messages.success(request,"Student Created Successfully")
                return redirect('list_student')
            else:
                Students.objects.filter(id=id).update(name=studnetname,mobile=studnetmobile,email=studnetemail,status=studnetstatus,department_id=studnetdept,address=studnetaddress)
                messages.success(request,"Student Updated Successfully")
                return redirect('list_student')
    if id!=0:
        student_data=Students.objects.filter(id=id).first()
    else:
        student_data=None

    department_data = Department.objects.filter(status=1).all().order_by("-id")
    context = {"department_data" : department_data,"student_data" : student_data}
    return render(request,"add-students.html" , context)


def list_student(request):
    student_data = Students.objects.all().order_by("-id")
    context = {"student_data" : student_data}
    student_id = request.GET.get("id")
    act = request.GET.get("act")
    if act == "delete" and student_id:
        Students.objects.filter(id=student_id).delete()
        messages.success(request,"Student Data Deleted Successfully")

    return render(request,"list-students.html", context)



def add_bill(request):
    if request.method=='POST':
        student_id = request.POST.get('student_id')
        order = Order_conf.objects.create(students_id=student_id)
        order_id =order.id
        qty_list = request.POST.getlist('qty[]')
        price_list = request.POST.getlist('price[]')
        product_list = request.POST.getlist('product_id[]')
        total_list = request.POST.getlist('total_id[]')
        gst_list = request.POST.getlist('gst[]')
        total_price = 0
        total_gst_amt = 0
        total_net = 0
        for i in range(len(product_list)):
            product_id = product_list[i]
            qty = int(qty_list[i])
            gst = gst_list[i]
            price = float(price_list[i])
            net_amount = float(total_list[i])
            gst_amt= (float(price)*float(gst))/100
            total_price =total_price+price
            total_gst_amt = total_gst_amt+gst_amt
            total_net =total_net+net_amount
            Order_products.objects.create(order_confirmation_id=order_id,products_id=product_id,price=price,qty=qty
                                         ,gst_per=gst,gst_amt=gst_amt,net_amount=net_amount)
        
        Order_conf.objects.filter(id=order_id).update(total_amt=total_price,gst_amt=total_gst_amt,net_amt=total_net)
        return redirect('list_bill')
    department_data = Department.objects.filter(status=1).all().order_by("-id")
    product_data = Products.objects.filter(status=1).all().order_by("-id")
    context = {"department_data" : department_data,"product_data" : product_data}
    return render(request,"add-bill.html",context)


def list_bill(request):
    return render(request,"list-bill.html")


def ajax_get_students(request):
    dept_id = request.POST.get("dept_id")
    student_data = Students.objects.filter(department_id=dept_id,status=1).all().order_by("-id")
    context = {"student_data" : student_data}
    return render(request,"ajax-student-list.html",context)


def get_product_price(request):
    product_id = request.GET.get('product_id')
    product = Products.objects.filter(id=product_id).first()
    if product:
        product_price= product.price
    else:
        product_price=0
    return HttpResponse(product_price)


def logout(request):
    request.session.flush()
    return redirect('login')

