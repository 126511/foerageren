from django import forms
from django.forms import ModelForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from myproject.models import *
from django.core.exceptions import ObjectDoesNotExist

def requires_login(view):
    def new_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(f'/accounts/login?next={request.path}') 
        return view(request, *args, **kwargs)
    return new_view 

def requires_superuser(view):
    def new_view(request, *args, **kwargs): 
        if not request.user.is_superuser: 
            messages.add_message(request, messages.INFO, 'Jij bent geen admin en mag deze pagina niet gebruiken!') 
            return HttpResponseRedirect('/')
        return view(request, *args, **kwargs)
    return new_view

def requires_profile(view):
    def new_view(request, *args, **kwargs): 
        profile = Profile.objects.filter(user=request.user).count()
        if profile < 1 or not Profile.objects.get(user=request.user).completed: 
            messages.add_message(request, messages.INFO, 'Maak eerst een profiel aan:') 
            return HttpResponseRedirect(f'/profile?next={request.path}')
        return view(request, *args, **kwargs)
    return new_view

def requires_group(view):
    def new_view(request, *args, **kwargs):
        p = Permission.objects.filter(user=request.user)
        if not p:
            messages.add_message(request, messages.INFO, 'Je zit nog niet in een groep')
            return HttpResponseRedirect('/new_group/')
        get_groups(request)
        if Permission.objects.get(user=request.user, group=request.user.current_group()).permission == 4:
            messages.add_message(request, messages.WARNING, 'Je bent uit deze groep verbannen! Wissel van groep of maak een nieuwe aan.')
            return render(request, 'banned.html')
        return view(request, *args, **kwargs)
    return new_view

def requires_manager(view):
    def new_view(request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        p = Permission.objects.get(user=request.user, group=profile.current_group)
        if p.permission >= 3:
            messages.add_message(request, messages.WARNING, 'Jij bent geen manager en mag deze pagina niet gebruiken!')
            return HttpResponseRedirect("/")
        return view(request, *args, **kwargs)
    return new_view

def requires_admin(view):
    def new_view(request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        p = Permission.objects.get(user=request.user, group=profile.current_group)
        if p.permission >= 2:
            messages.add_message(request, messages.WARNING, 'Jij bent geen admin en mag deze pagina niet gebruiken!')
            return HttpResponseRedirect("/")
        return view(request, *args, **kwargs)
    return new_view
            
def get_form(model_class,excludes):
    class DynamoForm(forms.ModelForm):
        class Meta:
            model = model_class
            exclude = excludes
   
    return DynamoForm

def form_config(model):
    if model == 'Product':
        excludes = ['group']
        title = 'Producten'
    elif model == 'Prepaid':
        excludes = ['processed', 'group']
        title = 'Opwaarderingen'        
    elif model == 'Stock':
        excludes = ['group', 'product']
        title = 'Voorraad'                           
    else:
        excludes = []
        title = 'Object'

    return excludes,title

def create(request,model):

    from django.apps import apps

    excludes,title = form_config(model)

    local_model = apps.get_model('myproject', str(model))

    if request.POST:
        form = get_form(local_model,excludes=excludes)(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save()
            if model == "Prepaid" or model == "Product":
                obj.group = request.user.current_group()
            obj.save()
            if model == "Stock":
                p = Product.objects.get(id=request.POST['product'])
                p.stock += int(request.POST['amount'])
                p.save()
        
            messages.add_message(request, messages.SUCCESS, 'Object succesvol toegevoegd.') 
            form = get_form(local_model,excludes=excludes)(request.POST)
        else:
            messages.add_message(request, messages.INFO, 'Er is iets fout gegaan.')            
    else:
        form = get_form(local_model,excludes=excludes)

    objects = local_model.objects.all()

    if model == "Product" or model == "Prepaid":
        objects = local_model.objects.filter(group=request.user.current_group())
    
    return render(request, 'create_form.html', {'objects':objects, 'form':form, 'title':title, 'model':model})

def products(request):

    def get_form(model_class,excludes):
        class DynamoForm(forms.ModelForm):
            class Meta:
                model = model_class
                exclude = excludes
            def __init__(self, *args, **kwargs):
                super(DynamoForm, self).__init__(*args, **kwargs)
        return DynamoForm
    
    excludes = ['group']
    title = 'Producten'

    if request.POST:
        form = get_form(Product,excludes=excludes)(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save()
            obj.group = request.user.current_group()
            obj.save()
        
            messages.add_message(request, messages.SUCCESS, 'Product succesvol toegevoegd.') 
            form = get_form(Product,excludes=excludes)(request.POST)
        else:
            messages.add_message(request, messages.WARNING, 'Er ging iets fout') 
    else:
        form = get_form(Product,excludes=excludes)

    objects = Product.objects.filter(group=request.user.current_group())

    return render(request, 'create_form.html', {'objects':objects, 'form':form, 'title':title, 'model':'Product'})

def stocks(request):
   
    def get_form(model_class,excludes):
        class DynamoForm(forms.ModelForm):
            class Meta:
                model = model_class
                exclude = excludes
            def __init__(self, *args, **kwargs):
                super(DynamoForm, self).__init__(*args, **kwargs)
                self.fields['product'].queryset = Product.objects.filter(group=request.user.current_group())
        return DynamoForm
    
    excludes = ['group']
    title = 'Voorraad'

    if request.POST:
        form = get_form(Stock,excludes=excludes)(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save()
            obj.group = request.user.current_group()
            obj.save()

            p = Product.objects.get(id=request.POST['product'])
            p.stock += int(request.POST['amount'])
            p.save()
        
            messages.add_message(request, messages.SUCCESS, 'Voorraad succesvol toegevoegd.') 
            form = get_form(Stock,excludes=excludes)(request.POST)
        else:
            messages.add_message(request, messages.WARNING, 'Er ging iets fout') 
    else:
        form = get_form(Stock,excludes=excludes)

    products = Product.objects.filter(group=request.user.current_group())
    objects = Stock.objects.filter(product__in=products)

    return render(request, 'create_form.html', {'objects':objects, 'form':form, 'title':title, 'model':'Stock'})

def prepaids(request):

    def get_form(model_class,excludes):
        class DynamoForm(forms.ModelForm):
            class Meta:
                model = model_class
                exclude = excludes
            def __init__(self, *args, **kwargs):
                super(DynamoForm, self).__init__(*args, **kwargs)
                allowed_buyers = Permission.objects.none()
                for p in Permission.objects.filter(group=request.user.current_group()):
                    allowed_buyers |= User.objects.filter(id=p.user.id)
                self.fields['buyer'].queryset = allowed_buyers
                self.fields['group'].initial = request.user.current_group()
                self.fields['group'].widget = forms.HiddenInput()
            
        return DynamoForm
    
    excludes = ['processed']
    title = 'Opwaarderingen'

    if request.POST:
        form = get_form(Prepaid,excludes=excludes)(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save()
            obj.group = request.user.current_group()
            obj.save()
      
            messages.add_message(request, messages.SUCCESS, 'Opwaardering succesvol toegevoegd.') 
            form = get_form(Prepaid,excludes=excludes)(request.POST)
        else:
            messages.add_message(request, messages.WARNING, 'Er ging iets fout') 
    else:
        form = get_form(Prepaid,excludes=excludes)

    objects = Prepaid.objects.filter(group=request.user.current_group())

    return render(request, 'create_form.html', {'objects':objects, 'form':form, 'title':title, 'model':'Prepaid'})

def edit(request,model,id):

    from django.apps import apps

    excludes,title = form_config(model)

    local_model = apps.get_model('myproject', str(model))
    instance = local_model.objects.get(id=id)

    if request.POST:
        form = get_form(local_model,excludes=excludes)
        form = form(request.POST,request.FILES,instance=instance)
        if form.is_valid():
            if model == "Stock":
                p = Product.objects.get(id=request.POST['product'])
                s = Stock.objects.get(id=id)
                difference = int(request.POST['amount']) - s.amount
                p.stock += difference
                p.save()
            
            if model == "Prepaid":
                b = Balance.objects.get(user=request.user, group=request.user.current_group())
                p = Prepaid.objects.get(id=id)
                difference = int(request.POST['amount']) - p.amount
                b.balance += difference
                b.save()
            
            obj = form.save()
            obj.save()

            messages.add_message(request, messages.SUCCESS, 'Object successvol upgedate.') 
        else:
            messages.add_message(request, messages.INFO, 'Er is iets fout gegaan.')            
    else:
        form = get_form(local_model,excludes=excludes)
        form = form(instance=instance)

    return render(request, 'edit_form.html', {'instance':instance, 'form':form, 'title':title, 'model':model})

def delete(request,model,id):

    from django.apps import apps

    if model == 'User':
        User.objects.get(id=id).delete()
        messages.add_message(request, messages.INFO, 'Gebruiker verwijderd.') 
        return HttpResponseRedirect('/users/') 
    if model == 'Sale':
        Sale.objects.get(id=id).delete()
        messages.add_message(request, messages.INFO, 'Aankoop ongedaan gemaakt.') 
        return HttpResponseRedirect('/')
    if model == 'Stock':
        s = Stock.objects.get(id=id)
        p = s.product
        p.stock -= s.amount
        p.save()
        s.delete()
        return HttpResponseRedirect('/stocks/')
    if model == "Invite":
        i = Invite.objects.get(id=id)
        i.delete()
        messages.add_message(request, messages.SUCCESS, 'Uitnodiging verwijderd.')
        return HttpResponseRedirect('/invite/')
    else:
        local_model = apps.get_model('myproject', str(model))
        instance = local_model.objects.get(id=id)
        instance.delete()
        messages.add_message(request, messages.INFO, 'Object verwijderd.') 

        return HttpResponseRedirect('/') 

def start(request):
    group = Profile.objects.get(user=request.user).current_group
    products = Product.objects.filter(group=group).order_by('name')
    users = Profile.objects.filter(current_group=group).exclude(user__id=1).order_by('-last_update')
    last_sale = None
    user_badges = []

    b, created = Balance.objects.get_or_create(user=request.user, group=group)
    request.session['balance'] = b.balance

    if request.POST:
        sales = 0
        buyers = []

        for buyer in users:
            if 'buyer-'+str(buyer.user.id) in request.POST:
                sales += 1
                sale = Sale()
                sale.cashier = request.user
                sale.buyer = buyer.user
                sale.product = Product.objects.get(id=int(request.POST['product']))
                sale.amount = int(request.POST['amount'])
                sale.group = group
                sale.save()
                buyers.append(buyer.user.id)
        if sales == 0:
            messages.add_message(request, messages.WARNING, 'Kies tenminste 1 persoon') 
        else:
            messages.add_message(request, messages.SUCCESS, 'Afgerekend :)')
            
            for buyer in buyers:
                user_badges = list(User_badge.objects.filter(user__id=buyer).values_list('badge__id',flat=True))
                for badge in Badge.objects.filter(product=Product.objects.get(id=int(request.POST['product']))).exclude(id__in=user_badges):
                    if badge.slug == 'n00b':
                        # n00b time
                        db_user = User.objects.get(id=buyer)
                        if Sale.objects.filter(product=badge.product,buyer=db_user).count()>=5:
                            user_badge = User_badge()
                            user_badge.badge = badge
                            user_badge.user = db_user
                            user_badge.save()
                            user_badges.append(user_badge.id)
                    if badge.slug == 'expert':
                        # expert time
                        db_user = User.objects.get(id=buyer)
                        if Sale.objects.filter(product=badge.product,buyer=db_user).count()>=100:
                            user_badge = User_badge()
                            user_badge.badge = badge
                            user_badge.user = db_user
                            user_badge.save()
                            user_badges.append(user_badge.id)                            
            user_badges = User_badge.objects.filter(id__in=user_badges)
        return HttpResponseRedirect("/")

    return render(request, 'start.html', {'products':products, 'users':users, 'last_sale':last_sale, 'user_badges':user_badges})

def history(request):
    users = Profile.objects.exclude(user__id=1).order_by('-last_update')
    if request.user.id == 1:
        sales = Sale.objects.all().order_by('-added_at')[:100]
    elif Permission.objects.get(user=request.user, group=request.user.current_group()).permission <= 2:
        from django.db.models import Q
        sales = Sale.objects.filter(Q(buyer=request.user) | Q(group=request.user.current_group()))[:100]
    else:
        sales = Sale.objects.filter(buyer=request.user).order_by('-added_at')[:100]
    return render(request, 'history.html', {'sales':sales, 'users':users})

def graph(request):
    users = Profile.objects.exclude(user__id=1).order_by('-last_update')
    if request.user.id == 1:
        sales = Sale.objects.all().order_by('-added_at')
    else:
        sales = Sale.objects.filter(buyer=request.user).order_by('-added_at')
    return render(request, 'graph.html', {'sales':sales, 'users':users})

def balance(request):
    prepaids = Prepaid.objects.filter(buyer=request.user, group=request.user.current_group())
    profile = Balance.objects.get(user=request.user, group=request.user.current_group())
    return render(request, 'balance.html', {'prepaids':prepaids, 'profile':profile})

def inventory(request):
    products = Product.objects.filter(group=request.user.current_group())
    return render(request, 'inventory.html', {'products':products})

def users(request):
    group = request.user.current_group()
    users = []
    for user in Profile.objects.filter(current_group=group).exclude(user__id=1).order_by('balance','-last_update'):
        permission = Permission.objects.get(user=user.user, group=group)
        balance = Balance.objects.get(user=user.user, group=group)
        users.append((user, balance, permission.verbose_permission()))
    return render(request, 'users.html', {'users':users})

def profile(request, *args, **kwargs):
    profile, created = Profile.objects.get_or_create(user=request.user)

    from django.contrib.admin.widgets import AdminDateWidget

    class ProfileForm(ModelForm):
        class Meta:
            model = Profile
            exclude = ['user','slug','status','completed','organization','intro_completed','group','feedback_user','score','balance','image','birth','current_group']
            widgets = {'birth':AdminDateWidget} 

    if request.POST:
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            obj = form.save()
            obj.save()
            if not obj.completed:
                obj.completed = True
                messages.add_message(request, messages.SUCCESS, 'Welkom bij Foerageren :)') 
                obj.save()
                if kwargs.get('next'):
                    return HttpResponseRedirect(f"/{kwargs['next']}")
                return HttpResponseRedirect('/') 

            messages.add_message(request, messages.SUCCESS, 'Profiel instellingen zijn successvol opgeslagen.') 
            profile = Profile.objects.get(user=request.user)
            form = ProfileForm(instance=profile) 
        else:
            messages.add_message(request, messages.INFO, 'Er is iets fout gegaan.')            
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'profile':profile, 'form':form})

def new_group(request):
    class GroupForm(ModelForm):
        class Meta:
            model = Group
            exclude = ['is_official', 'members']

    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            from django.db import IntegrityError
            try:
                obj = form.save()
            except IntegrityError:
                messages.add_message(request, messages.INFO, 'Die groep bestaat al')
                return HttpResponseRedirect("/")

            p = Permission.objects.create(user=request.user, group=obj, permission=1)
            p.save()

            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.current_group = obj
            profile.save()

            messages.add_message(request, messages.SUCCESS, 'Je groep is opgeslagen, jij bent Manager van deze groep') 
            return HttpResponseRedirect("/")
        else:
            messages.add_message(request, messages.INFO, 'Er is iets fout gegaan.')
            return HttpResponseRedirect("/")   
    else:
        form = GroupForm()
        groups = Group.objects.filter(is_open=True)
        return render(request, 'new_group.html', {'groups': groups, 'form': form})

def join_group(request, id):
    g = Group.objects.filter(id=id)
    if not g:
        messages.add_message(request, messages.WARNING, "Die groep bestaat niet!")
        return HttpResponseRedirect("/")
    g = g[0]

    if not g.is_open:
        messages.add_message(request, messages.WARNING, "Je mag alleen deelnemen aan deze groep met een uitnodiging!")
        return HttpResponseRedirect("/")
    
    p = Permission(user=request.user, group=g)
    p.save()

    profile = Profile.objects.get(user=request.user)
    profile.current_group = g
    profile.save()

    messages.add_message(request, messages.SUCCESS, f"Je bent toegevoegd aan {g.name}!")
    return HttpResponseRedirect("/")

def get_groups(request):
    permissions = Permission.objects.filter(user=request.user)
    groups = {}
    for p in permissions:
        groups[p.group.name] = (p.verbose_permission(), p.group.id)
    
    profile = Profile.objects.get(user=request.user)
    if profile.current_group:
        request.session['current_group'] = profile.current_group.name

    request.session['groups'] = groups

def switch_group(request, new_group):
    profile = Profile.objects.get(user=request.user)
    p = Permission.objects.filter(user=request.user)

    try:
        g = Group.objects.get(id=new_group)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING, "Die groep bestaat niet!")
        return HttpResponseRedirect("/")

    for permission in p:
        if permission.group == g:
            profile.current_group = g
            profile.save()

            messages.add_message(request, messages.SUCCESS, 'Je bent van groep gewisseld!')
            return HttpResponseRedirect("/")
    
    messages.add_message(request, messages.ERROR, 'Jij zit niet in die groep!')
    return HttpResponseRedirect("/")

def ban_user(request, id):
    banned_user = User.objects.filter(id=id)
    if not banned_user:
        messages.add_message(request, messages.ERROR, 'Die gebruiker bestaat niet!')
        return HttpResponseRedirect('/users')
    banned_user = banned_user.first()

    group = request.user.current_group()

    p = Permission.objects.filter(user=banned_user, group=group)
    if not p:
        messages.add_message(request, messages.WARNING, 'Die gebruiker zit niet in deze groep!')
        return HttpResponseRedirect('/users')
    p = p.first()

    print(p.permission)

    if p.permission <= 2 and not request.user.is_superuser:
        messages.add_message(request, messages.ERROR, 'Alleen superusers mogen managers of admins verbannen!')
        return HttpResponseRedirect('/users')
    
    p.permission = 4
    p.save()

    messages.add_message(request, messages.SUCCESS, 'Gebruiker verbannen')
    return HttpResponseRedirect('/users')

def unban_user(request, id):
    banned_user = User.objects.filter(id=id)
    if not banned_user:
        messages.add_message(request, messages.ERROR, 'Die gebruiker bestaat niet!')
        return HttpResponseRedirect('/users')
    banned_user = banned_user.first()

    group = request.user.current_group()

    p = Permission.objects.filter(user=banned_user, group=group)
    if not p:
        messages.add_message(request, messages.WARNING, 'Die gebruiker zit niet in deze groep!')
        return HttpResponseRedirect('/users')
    p = p.first()

    if p.permission != 4:
        messages.add_message(request, messages.WARNING, 'Die gebruiker is niet verbannen')
        return HttpResponseRedirect('/users')
    
    p.permission = 3
    p.save()

    messages.add_message(request, messages.SUCCESS, 'Gebruiker is niet meer verbannen')
    return HttpResponseRedirect('/users')

def invite(request):



    invites = Invite.objects.filter(group=request.user.current_group())

    return render(request, 'invite.html', {'invites': invites})

def new_invite(request):
    def generate_key():
        import random, string
        return "".join(random.choice(string.ascii_letters + string.digits) for x in range(16))
    
    i = Invite(key=generate_key(), group=request.user.current_group(), requested_by=request.user)
    i.save()

    invites = Invite.objects.filter(group=request.user.current_group())

    return render(request, 'invite.html', {'invites': invites, 'new_invite': i})

def use_invite(request, key, *args, **kwargs):
    try:
        i = Invite.objects.get(key=key)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Dat is geen geldige link!')
        return HttpResponseRedirect('/profile')
    
    g = i.group
    
    p, created = Permission.objects.get_or_create(user=request.user, group=g)
    p.save()

    profile = Profile.objects.get(user=request.user)
    profile.current_group = g
    profile.save()

    messages.add_message(request, messages.SUCCESS, f"Je bent toegevoegd aan {g.name}!")
    return HttpResponseRedirect("/")

def remove_user(request, user_id):
    group = request.user.current_group()

    try:
        removee = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING, "Deze gebruiker bestaat niet!")
        return HttpResponseRedirect('/users')
    
    try:
        p = Permission.objects.get(user=removee, group=group)

        if p.permission <= Permission.objects.get(user=request.user, group=group).permission:
            messages.add_message(request, messages.WARNING, "Jij mag deze gebruiker niet verwijderen")
            return HttpResponseRedirect("/users")
        
        p.delete()

        profile = Profile.objects.get(user=removee)
        profile.current_group = None
        profile.save()

        try:
            balance = Balance.objects.get(user=removee, group=group)
            balance.delete()
        except ObjectDoesNotExist:
            pass

        messages.add_message(request, messages.SUCCESS, "Gebruiker verdwijderd.")
        return HttpResponseRedirect("/users")

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Deze gebruiker zit niet in jouw groep!")
        return HttpResponseRedirect("/users")

def make_manager(request, user_id):
    group = request.user.current_group()

    try:
        managee = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING, "Deze gebruiker bestaat niet!")
        return HttpResponseRedirect('/users')

    try:
        p = Permission.objects.get(user=managee, group=group)
        if p.permission <= 2:
            messages.add_message(request, messages.warning, "Deze gebruiker is al manager of admin en kan je dus geen manager maken!")
            return HttpResponseRedirect("/users")

        p.permission = 2
        p.save()

        messages.add_message(request, messages.SUCCESS, f"Je hebt {managee} manager gemaakt van {group}!")
        return HttpResponseRedirect("/users")
    
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, f"Deze gebruiker zit niet in {group}!")
        return HttpResponseRedirect("/users")

def remove_manager(request, user_id):
    group = request.user.current_group()

    try:
        managee = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING, "Deze gebruiker bestaat niet!")
        return HttpResponseRedirect('/users')

    try:
        p = Permission.objects.get(user=managee, group=group)
        if p.permission <= 2:
            messages.add_message(request, messages.warning, "Deze gebruiker is al manager of admin en kan je dus geen manager maken!")
            return HttpResponseRedirect("/users")

        p.permission = 2
        p.save()

        messages.add_message(request, messages.SUCCESS, f"Je hebt {managee} manager gemaakt van {group}!")
        return HttpResponseRedirect("/users")
    
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, f"Deze gebruiker zit niet in {group}!")
        return HttpResponseRedirect("/users")


    

    
