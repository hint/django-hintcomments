(function($) {
    $.fn.hintCommentPagination = function(options) {

        var opts = $.extend({}, $.fn.hintCommentPagination.defaults, options);
        var params = ['current_page','items_per_page','link_to','num_display_entries','next_text','next_show_always',
            'prev_text','prev_show_always','num_edge_entries','ellipse_text']

        return this.each(function() {
            var container = $(this);
            var comments = container.find(container.find("input[name='comments_selector']").val());
            if (comments === "") {
                return;
            }
            var items_per_page = parseInt(container.find("input[name='items_per_page']").val());
            var pag_container = container.find(".pagination-container");

            var settings = {};
            for (var i = 0; i < params.length; i++) {
                settings[params[i]] = container.find("input[name='" + params[i] + "']").val()
            }

            function handlePaginationClick(new_page_index, pagination_container) {
                var first_index = new_page_index * items_per_page;
                var last_index = Math.min((new_page_index + 1 ) * items_per_page, comments.length);

                comments.hide();

                for (var i = first_index; i < last_index; i++) {
                    comments.filter(":eq(" + i + ")").show();
                }
                return false;
            }

            settings['callback'] = handlePaginationClick;

            $(pag_container).pagination(comments.length, settings);
        });
    };

    $.fn.hintCommentForm = function(options) {

        var opts = $.extend({}, $.fn.hintCommentForm.defaults, options);

        return this.each(function() {
            var form = $(this);
            var action = form.attr("action");
            form.submit(function(e) {
                e.preventDefault();

                $("#comment-form").ajaxSend(function(event, xhr, settings) {
                    function getCookie(name) {
                        var cookieValue = null;
                        if (document.cookie && document.cookie != '') {
                            var cookies = document.cookie.split(';');
                            for (var i = 0; i < cookies.length; i++) {
                                var cookie = jQuery.trim(cookies[i]);
                                // Does this cookie string begin with the name we want?
                                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                    break;
                                }
                            }
                        }
                        return cookieValue;
                    }


                    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                        // Only send the token to relative URLs i.e. locally.
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                });

                $("#comment-form").ajaxError(function(event, request, settings, error) {
                    console.log(request.status);

                    if($.trim(request.responseText) === ""){
                        alert("Error while loading comment. Please refresh the page.");
                        return false;
                    }
                    var new_form = $(request.responseText);
                    $(this).replaceWith(new_form);
                    new_form.hintCommentForm();
                });

                $.post(action, form.serialize(), function(data, textStatus, jqXHR) {
                    $("#ajax-comment-list-holder").hide().html(data).hintCommentPagination().fadeIn();
                });

                return false;
            });
        });
    };

    $.fn.hintComments = function(options) {
        return this.each(function() {
            $(this).hintCommentForm();
            $("#ajax-comment-list-holder").hintCommentPagination();
        });
    };
})(jQuery);