(function($) {
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
                    $("#ajax-comment-list-holder").hide().html(data).fadeIn();

                    form.find("[name]:not(:hidden)").filter("[type!='submit']").filter("[type!='button']").each(function(){
                        $(this).val("");
                    })
                });

                return false;
            });
        });
    };
})(jQuery);