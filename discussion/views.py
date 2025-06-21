from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .models import Discussion, Reply
from .forms import DiscussionForm, ReplyForm
from django.http import JsonResponse

# Explore all discussions
@login_required
def discussion_list(request):
    discussions = Discussion.objects.all().order_by('-created_at')
    return render(request, 'discussion/discussion_list.html', {'discussions': discussions})

# View user's own posts
@login_required
def your_posts(request):
    discussions = Discussion.objects.filter(user=request.user)\
                                    .prefetch_related('replies')\
                                    .order_by('-created_at')
    return render(request, 'discussion/your_posts.html', {'discussions': discussions})

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

# Edit discussion (modal only)
# @login_required
# def edit_discussion(request, pk):
#     discussion = get_object_or_404(Discussion, pk=pk)
#     if request.user != discussion.user:
#         return HttpResponseForbidden()

#     if request.method == 'POST':
#         form = DiscussionForm(request.POST, request.FILES, instance=discussion)
#         if form.is_valid():
#             form.save()
#             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return HttpResponse('<script>closeModal(); window.location.reload();</script>')
#             return redirect('discussion_list')
#     else:
#         form = DiscussionForm(instance=discussion)

#     return render(request, 'discussion/discussion_form_modal.html', {'form': form, 'action': 'Edit'})
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
