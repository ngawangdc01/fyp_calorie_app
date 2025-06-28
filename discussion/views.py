from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Discussion, Reply
from .forms import DiscussionForm, ReplyForm
from django.http import JsonResponse

# Explore all discussions
@login_required
def discussion_list(request):
    discussions = Discussion.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(discussions, 10)  # Show 10 discussions per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        page_obj = paginator.page(paginator.num_pages)
    
    # Calculate page range for display (show max 5 page buttons)
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    # Logic for displaying page numbers
    if total_pages <= 5:
        # If 5 or fewer pages, show all
        page_range = range(1, total_pages + 1)
        show_first_ellipsis = False
        show_last_ellipsis = False
    else:
        # More than 5 pages, need to be selective
        if current_page <= 3:
            # Near the beginning
            page_range = range(1, 4)
            show_first_ellipsis = False
            show_last_ellipsis = True
        elif current_page >= total_pages - 2:
            # Near the end
            page_range = range(total_pages - 2, total_pages + 1)
            show_first_ellipsis = True
            show_last_ellipsis = False
        else:
            # In the middle
            page_range = range(current_page - 1, current_page + 2)
            show_first_ellipsis = True
            show_last_ellipsis = True
    
    context = {
        'discussions': page_obj,
        'page_obj': page_obj,
        'page_range': page_range,
        'show_first_ellipsis': show_first_ellipsis,
        'show_last_ellipsis': show_last_ellipsis,
    }
    
    return render(request, 'discussion/discussion_list.html', context)

# View user's own posts
@login_required
def your_posts(request):
    discussions = Discussion.objects.filter(user=request.user)\
                                    .prefetch_related('replies')\
                                    .order_by('-created_at')
    
    # Pagination for user's posts
    paginator = Paginator(discussions, 10)  # Show 10 discussions per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Calculate page range for display (show max 5 page buttons)
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    if total_pages <= 5:
        page_range = range(1, total_pages + 1)
        show_first_ellipsis = False
        show_last_ellipsis = False
    else:
        if current_page <= 3:
            page_range = range(1, 4)
            show_first_ellipsis = False
            show_last_ellipsis = True
        elif current_page >= total_pages - 2:
            page_range = range(total_pages - 2, total_pages + 1)
            show_first_ellipsis = True
            show_last_ellipsis = False
        else:
            page_range = range(current_page - 1, current_page + 2)
            show_first_ellipsis = True
            show_last_ellipsis = True
    
    context = {
        'discussions': page_obj,
        'page_obj': page_obj,
        'page_range': page_range,
        'show_first_ellipsis': show_first_ellipsis,
        'show_last_ellipsis': show_last_ellipsis,
    }
    
    return render(request, 'discussion/your_posts.html', context)

# View a discussion (modal only)
@login_required
def discussion_detail(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    replies = discussion.replies.all().order_by('created_at')

    if request.method == 'POST':
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.discussion = discussion
            reply.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('<script>window.location.reload();</script>')
            return redirect('discussion_list')
    else:
        form = ReplyForm()

    context = {
        'discussion': discussion,
        'replies': replies,
        'form': form,
    }

    return render(request, 'discussion/discussion_detail_modal.html', context)

# Create new discussion (modal only)
@login_required
def create_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST, request.FILES)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.user = request.user
            discussion.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('<script>closeModal(); window.location.reload();</script>')
            return redirect('discussion_list')
    else:
        form = DiscussionForm()

    return render(request, 'discussion/discussion_form_modal.html', {'form': form, 'action': 'Create'})

@login_required
def edit_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    if request.user != discussion.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        # Check if user requested to clear the image
        if request.POST.get('clear_image') == 'true':
            if discussion.image:
                discussion.image.delete(save=False)
            discussion.image = None  # Reset field

        form = DiscussionForm(request.POST, request.FILES, instance=discussion)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('<script>closeModal(); window.location.reload();</script>')
            return redirect('discussion_list')
    else:
        form = DiscussionForm(instance=discussion)

    return render(request, 'discussion/discussion_edit_form_modal.html', {
        'form': form,
        'discussion': discussion,
    })

# Delete discussion
@login_required
def delete_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    if request.user == discussion.user:
        discussion.delete()
    return redirect('discussion_list')

# Edit reply (modal only)
@login_required
def edit_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.user != reply.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ReplyForm(request.POST, request.FILES, instance=reply)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('<script>window.location.reload();</script>')
            return redirect('discussion_list')
    else:
        form = ReplyForm(instance=reply)

    return render(request, 'discussion/reply_form_modal.html', {'form': form})

# Delete reply
@login_required
def delete_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.user == reply.user:
        reply.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('discussion_list')
    return HttpResponseForbidden()