$(document).ready(function() {
    $('#like_btn').click(function() {
        var categoryIdVar;
        categoryIdVar = $(this).attr('data-categoryid');

        $.get(url='/rango/like_category/',
            {'category_id': categoryIdVar},
            function(data) {
                $('#like_count').html(data);
                $('#like_btn').hide();
            })
    });

    $('#search-input').keyup(function() {
        console.log('ready')
        var query;
        query = $(this).val();

        $.get(url='/rango/suggest/',
            {'suggestion': query},
            function(data) {
                $('#categories-listing').html(data);
            })
    });

    $('.search-page-add').click(function() {
        var pageURL = $(this).attr('data-url');
        var title = $(this).attr('data-title');
        var categoryId = $(this).attr('data-categoryid');
        var clickedButton = $(this)

        $.get(url='/rango/search_add_page/',
            {'page_url': pageURL, 'title': title, 'category_id': categoryId},
            function(data) {
                $('#list_pages').html(data);
                clickedButton.hide();
        })
    });
})