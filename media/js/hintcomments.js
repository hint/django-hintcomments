(function($) {
    $.fn.hintCommentPagination = function(options) {

        var opts = $.extend({}, $.fn.hintCommentPagination.defaults, options);

        return this.each(function() {
            var container = $(this);
            var comments = container.find(container.find("input[name='comments_selector']").val());
            if (comments === ""){
                return;
            }
            var items_per_page = parseInt(container.find("input[name='paginate_by']").val());

            var pag_container = container.find(".pagination-container");

            function handlePaginationClick(new_page_index, pagination_container) {
                var first_index = new_page_index * items_per_page;
                var last_index = Math.min((new_page_index + 1 ) * items_per_page, comments.length);

                comments.hide();

                for (var i = first_index; i < last_index; i++) {
                    comments.filter(":eq(" + i + ")").show();
                }
                return false;
            }


            $(pag_container).pagination(comments.length, {
                        items_per_page: items_per_page,
                        callback:handlePaginationClick
                    });
        });
    };

    $.fn.hintCommentForm = function(options) {

        var opts = $.extend({}, $.fn.hintCommentForm.defaults, options);

        return this.each(function() {
            var form = $(this);
            var action = form.attr("action");
            form.submit(function(e) {
                e.preventDefault();

                $("#ajax-comment-list-holder").ajaxError(function(event, request, settings, error) {
                    alert("There were problems while loading requested data. Please try again or contact administrator");
                });

                $.post(action, form.serialize(), function(data, textStatus, jqXHR) {
                    $("#ajax-comment-list-holder").hide().html(data).hintCommentPagination().fadeIn();
                });

                return false;
            });
            $("#ajax-comment-list-holder").hintCommentPagination();
        });
    };
})(jQuery);