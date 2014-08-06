$( document ).ready(function() {

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

   (function checker(){

        function onSuccess(location){

            //Avoid doing any actions on pages that don't matter
            var url = window.location.pathname;
            if(url != "/feed/index.html"){
                return
            }

            //Geolocation did not work
            if(location == null){
                return;
            }
            
            //Get the radius
            radius = $("#radiusSelect").val(); 

            ids = new Array()
            $( ".eventRow" ).each(function( index ) {
                ids[index]=$(this).attr("eid");
            });
            idsJSON = JSON.stringify(ids);
            if(idsJSON==[]) return ;


            var dataJSON = {"csrfmiddlewaretoken":getCookie('csrftoken'),
            "lng":location.coords.longitude,
            "lat":location.coords.latitude,
            "radius":radius,
            "ids":idsJSON };


            $.ajax({
                type: "GET",
                url: "updateFeed",
                data: dataJSON,
                dataType: 'xml',
                success: function(xml){
                    $('#feedTable').empty();

                    $(xml).find("feed").each(function(){
                        name = $(this).find("name").text();
                        distance = $(this).find("distance").text();
                        description = $(this).find("description").text()
                        start = $(this).find("start").text()
                        end = $(this).find("end").text()
                        eventID = $(this).find("id").text()
                        longitude = $(this).find("longitude").text()
                        latitude = $(this).find("latitude").text()


          newRow ='<div id="event-'+eventID+'" class="post-entry">\
                      <center>\
                        <div class="event-text">\
                          <a href="/events/eventpage'+eventID+'">'+name+'</a></div>\
                          <p class="description">'+description+'</p>\
                          <p class="post-menu user"><b>'+distance+'</b></p>\
                        <p> <small>'+start+'-</small></p>\
                        <p> <small>'+end+'</small></p>\
                        </div>\
                    </center>\
                   <hr class="thin" style="margin-right:5%; padding-right:10%"/> '
                       $('#feedTable').append(newRow);
                    });
                },
                error: function(data){
                }
            });
        }

        //get the user's locations
        if(navigator.geolocation)
            navigator.geolocation.getCurrentPosition(onSuccess, function(){return;});
        else
            alert("Location not found. Please allow EventFinder to track your location");
        
        setTimeout(checker, 1000);
    })();
    $('.basic').fancySelect();
});


