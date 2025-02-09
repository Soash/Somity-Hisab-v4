from django.shortcuts import get_object_or_404, render, redirect
from app1.models import Branch
from django.shortcuts import render, redirect
from .forms import BranchForm
from django.contrib import messages

def branch_list(request):
    branches = Branch.objects.all()
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch added successfully.')
            return redirect('branch_list')  # Redirect to the same page or to a different page
    else:
        form = BranchForm()
        
    context = {
        'form': form,
        'branches': branches,
    }
    return render(request, 'primary_setup/branch_list.html', context)

def branch_list_edit(request, pk):
    branches = Branch.objects.all()
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            return redirect('branch_list')
    else:
        form = BranchForm(instance=branch)
    
    context = {
        'form': form,
        'branches': branches,
        'branch': branch,
    }
    return render(request, 'primary_setup/branch_edit.html', context)


