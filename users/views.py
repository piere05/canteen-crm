from genericpath import exists
from itertools import product
from urllib import request, response
from django.db.models import F, DecimalField, Sum , Count
from django.db.models.functions import Coalesce, Round
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import *
from django.template.loader import render_to_string

import datetime 
from datetime import date

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
         total_students = Students.objects.count()
         total_department = Department.objects.count()
         total_products = Products.objects.count()
         total_orders = Order_conf.objects.count()
         total_amt = Order_conf.objects.aggregate(Sum('net_amt'))
         
         context = {"total_students" : total_students, "total_department" : total_department, 
                    "total_products" : total_products
                    ,"total_orders" : total_orders,"total_amt" : total_amt}
         return render(request ,'home.html', context)


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
    
    if act=='order_product' and request.method== "POST":
        if int(id_val)!=0:
            order_product_data = Order_products.objects.filter(order_confirmation_id=id_val).annotate(
                product_amt  = F('price')*F('qty'),
                gst_amts  = Round((F('price')*F('qty')) * F('gst_per')/100,2),
                nett_tot = Round((F('price')*F('qty')) + (F('price')*F('qty')) * F('gst_per')/100,2),
            )
            totals = order_product_data.aggregate(total_productamt=Sum('product_amt'), grand_total=Sum('nett_tot'))
            context = {"act" : "order_product" , "order_product_data" :order_product_data ,  "totals": totals }
        else:
            context = {"act" : "order_product"}
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
    department_data = Department.objects.filter(status=1).all().order_by("-id")
    context = {"department_data" : department_data}
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



def add_bill(request,id=0):
    if int(id)!=0:
        order_data = Order_conf.objects.filter(id=id).first()
        order_product_data = Order_products.objects.filter(order_confirmation_id=id)
    else:
        order_data =''
        order_product_data=''
    if request.method=='POST':
        student_id = request.POST.get('student_id')
        if int(id)!=0:
            order = Order_conf.objects.filter(id=id).update(students_id=student_id)
            order_id =id
            Order_products.objects.filter(order_confirmation_id=id).delete()
            messages.success(request,"Bill Updated Successfully")
        else:
            order = Order_conf.objects.create(students_id=student_id)
            messages.success(request,"Bill Created Successfully")
            order_id =order.id # type: ignore
        qty_list = request.POST.getlist('qty[]')
        price_list = request.POST.getlist('price[]')
        product_list = request.POST.getlist('product_id[]')
        total_list = request.POST.getlist('total[]')
        gst_list = request.POST.getlist('gst[]')
        total_price = 0
        total_gst_amt = 0
        total_net = 0
        product_count =0
        for product_id, qty, price, total, gst in zip(product_list, qty_list, price_list, total_list, gst_list):
            qty = int(qty)
            price = float(price)
            gst = float(gst)
            product_count =product_count+1
            item_price = price * qty
            net_amount = float(total)
            gst_amt = (item_price * gst) / 100
            total_price =total_price+item_price
            total_gst_amt = total_gst_amt+gst_amt
            total_net =total_net+net_amount
            Order_products.objects.create(order_confirmation_id=order_id,products_id=product_id,price=price,qty=qty
                                         ,gst_per=gst,gst_amt=gst_amt,net_amount=net_amount)
        Order_conf.objects.filter(id=order_id).update(total_amt=total_price,gst_amt=total_gst_amt,net_amt=total_net,product_count=product_count)
        
        return redirect('list_bill')
    department_data = Department.objects.filter(status=1).all().order_by("-id")
    product_data = Products.objects.filter(status=1).all().order_by("-id")
    context = {"department_data" : department_data,"product_data" : product_data,"order_data" : order_data,"order_product_data" :order_product_data}
    return render(request,"add-bill.html",context)


def list_bill(request):
    bill_id = request.GET.get("id")
    act = request.GET.get("act")
    if act == "delete" and bill_id:
        Order_conf.objects.filter(id=bill_id).delete()
        messages.success(request,"Bill Deleted Successfully")
    billdata = Order_conf.objects.all().order_by("-id")
    context = {"billdata" : billdata}
    return render(request,"list-bill.html", context)


def ajax_get_students(request):
    dept_id = request.POST.get("dept_id")
    order_id = request.POST.get("order_id")
    student_data = Students.objects.filter(department_id=dept_id,status=1).all().order_by("-id")
    if order_id!='':
        student_selected = Order_conf.objects.filter(id=order_id).first()
        student_id=student_selected.students.id # type: ignore
    else:
        student_id=''
    context = {"student_data" : student_data,"student_id" : student_id}
    return render(request,"ajax-student-list.html",context)


def get_product_price(request):
    product_id = request.GET.get('product_id')
    product = Products.objects.filter(id=product_id).first()
    if product:
        product_price= product.price
    else:
        product_price=0
    return HttpResponse(product_price)



def change_password(request):
    user_id = request.session['user_id']
    if request.method=='POST':
        select_old = Users.objects.get(id=user_id)
        old_pass = request.POST.get("old_password")
        new_pass = request.POST.get("new_password")
        confirm_pass = request.POST.get("confirm_password")
        if select_old.password ==old_pass: # type: ignore
            if new_pass == confirm_pass:
                select_old.password = new_pass
                select_old.save()
                messages.success(request,"Password Successfully Changed")
                return redirect('change_password')
            else:             
                messages.error(request,"New and Confirm Password Didn't Match ")
                return redirect('change_password')
        else:
            messages.error(request,'Old Password is Incorrect')
            return redirect('change_password')
    return render(request,'change-password.html')

def dept_query(request):
        department_data = Department.objects.all()

        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        today = date.today() 
        if not from_date and not to_date:
            from_date = today.replace(day=1).strftime("%Y-%m-%d")
            to_date = today.strftime("%Y-%m-%d")
        if from_date and to_date:
            department_data = department_data.filter(students__order_conf__created_datetime__date__range=[from_date, to_date])
        department_data = department_data.annotate(
        total_students =Count('students'),
        total_order = Count('students__order_conf__students', distinct=True),
        dept_sales = Coalesce(Sum('students__order_conf__net_amt'),0, output_field=DecimalField()))
        return department_data, from_date, to_date
def dept_sales(request):
    department_data, from_date, to_date = dept_query(request)
    context = {"department_data" : department_data , "from_date" : from_date , "to_date" : to_date}
    return render(request,'department-sales.html',context)


def export_pdf(request):

    department_data = Department.objects.all()

    template = get_template("export-bill.html")
    html = template.render({
        "department_data": department_data
    })

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename="department_report.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response


def student_sales(request):
    department_data = Students.objects.annotate(
        total_order = Count('order_conf', distinct=True),
        dept_sales = Coalesce(Sum('order_conf__net_amt'),0, output_field=DecimalField())
    )       
    context = {"department_data" : department_data}
    return render(request,'students-sales.html',context)


def product_sales(request):
    product_data = Products.objects.annotate(
        total_qty = Coalesce(Sum('order_products__qty'),0),
        total_amt = Coalesce(Sum('order_products__net_amount'),0, output_field=DecimalField())
    )
    context = {"department_data" : product_data}
    return render(request, 'product-sales.html', context)

def export_dept_sales(request,type):
        if type=='department':
            department_data, from_date, to_date = dept_query(request)
            context = {"department_data" : department_data , "from_date" : from_date , "to_date" : to_date ,"type" :type}  
            html = render_to_string(
                'export-department-sales.html',
                context)
            response = HttpResponse(html, content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="department_sales.xls"'
            return response
        elif type=='students':
            department_data = Students.objects.annotate(
            total_order = Count('order_conf', distinct=True),
            dept_sales = Coalesce(Sum('order_conf__net_amt'),0, output_field=DecimalField())
            ) 
            context = {"department_data" : department_data ,"type" :type} 
            html = render_to_string(
                'export-department-sales.html',
                context)
            response = HttpResponse(html, content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="student_sales.xls"'
            return response
        elif type=='product':
            product_data = Products.objects.annotate(
            total_qty = Coalesce(Sum('order_products__qty'),0),
            total_amt = Coalesce(Sum('order_products__net_amount'),0, output_field=DecimalField()))
            context = {"department_data" : product_data ,"type" :type} 
            html = render_to_string(
                'export-department-sales.html',
                context)
            response = HttpResponse(html, content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="product_sales.xls"'
            return response

def logout(request):
    request.session.flush()
    return redirect('login')

