//Code adapted from google maps api examples


// This example adds a search box to a map, using the
// Google Places autocomplete feature. People can enter geographical searches.
// The search box will return a pick list containing
// a mix of places and predicted search terms.
$( document ).ready(function() {

var map;
var selectedPositon;
var markers = [];

function initialize() {
  //Avoid this function on pages that don't use the map
  if(document.getElementById('map-canvas') == null)
      return;

  //Initialize the map
  map = new google.maps.Map(document.getElementById('map-canvas'), {
    mapTypeId: google.maps.MapTypeId.ROADMAP
  });
  
 /* var defaultBounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(-33.8902, 151.1759),
      new google.maps.LatLng(-33.8474, 151.2631));
  map.fitBounds(defaultBounds);*/

  function onSuccess(location){
    //Set the map location to the users location
    var defaultBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(location.coords.latitude,location.coords.longitude),
        new google.maps.LatLng(location.coords.latitude,location.coords.longitude));

    map.fitBounds(defaultBounds);

  }

  function onErr(){
    //Use a hardcoded location if the user's location can't be found right now
    sydneylat1 = -33.8902;
    syndeylong1 = 151.1759;
    sydneylat2 = -33.8902;
    syndeylong2 = 151.1759;

    var defaultBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(sydneylat1, syndeylong1),
        new google.maps.LatLng(sydneylat2, syndeylong2));
    map.fitBounds(defaultBounds);

  }
  navigator.geolocation.getCurrentPosition(onSuccess, onErr);

  // Create the search box and link it to the UI element.
  var input = document.getElementById('target');
  var searchBox = new google.maps.places.SearchBox(input);

  // Begin google maps example 
  // [START region_getplaces]
  // Listen for the event fired when the user selects an item from the
  // pick list. Retrieve the matching places for that item.
  google.maps.event.addListener(searchBox, 'places_changed', function() {
    var places = searchBox.getPlaces();

    for (var i = 0, marker; marker = markers[i]; i++) {
      marker.setMap(null);
    }

    // For each place, get the icon, place name, and location.

    var bounds = new google.maps.LatLngBounds();
    for (var i = 0, place; place = places[i]; i++) {
      var image = {
        url: place.icon,
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(17, 34),
        scaledSize: new google.maps.Size(25, 25)
      };
      bounds.extend(place.geometry.location);
    }
    map.fitBounds(bounds);
  });


  // [END region_getplaces]

  // Bias the SearchBox results towards places that are within the bounds of the
  // current map's viewport.
  google.maps.event.addListener(map, 'bounds_changed', function() {
    var bounds = map.getBounds();
    searchBox.setBounds(bounds);
  });
//End google maps example


  //Clear markers and place the new one 
  google.maps.event.addListener(map, 'click', function(event) {
    //delete the current markers.
    for (var i = 0, marker; marker = markers[i]; i++) {
      marker.setMap(null);
    }

    placeMarker(event.latLng);
  });

}

//Found something similar on stack overflow
function placeMarker(location) {
  var marker = new google.maps.Marker({
      position: location,
      map: map
  });
  //add to marker array so we can delete it later.
  markers.push(marker);
  map.setCenter(location);
}

//Taken from google maps api examples
function handleNoGeolocation(errorFlag) {
  if (errorFlag) {
    var content = 'Error: The Geolocation service failed.';
  } else {
    var content = 'Error: Your browser doesn\'t support geolocation.';
  }

  var options = {
    map: map,
    position: new google.maps.LatLng(60, 105),
    content: content
  };

  var infowindow = new google.maps.InfoWindow(options);
  map.setCenter(options.position);
}


google.maps.event.addDomListener(window, 'load', initialize);

//Validate date

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



    //Update comments with ajax
    $('.createForm').submit(function(e){
         e.preventDefault(); //Prevent the normal submission action
         var form = this;
        //Validate user input

        latitude = JSON.stringify(map.getCenter().lat());
        longitude = JSON.stringify(map.getCenter().lng());

         var name = $("input[name='name']",form).val();
         var description = $("input[name='description']",form).val();
         var start = $("input[name='start']",form).val();
         var end = $("input[name='end']",form).val();
         var tags = $("input[name='tags']",form).val();
         var plugin = $("select[name='plugin']",form).val();

          var allJSON = {"csrfmiddlewaretoken":getCookie('csrftoken'),
          "lat":latitude,
          "lng":longitude,
          "name" : name,
          "description": description,
          "start": start,
          "end": end,
          "tags": tags,
          "plugin": plugin};

         // alert(start);
         var emptyErr = false;
         var errorMsg = "The following fields cannot be blank: \n";
         if (name == "") {
          emptyErr=true;
          errorMsg += "\t- Name \n"
         }
         if (description == "") {
          emptyErr=true;
          errorMsg += "\t- Description \n"
         }         
         if (start == "") {
          emptyErr=true;
          errorMsg += "\t- Start \n"
         }         
         if (end == "") {
          emptyErr=true;
          errorMsg += "\t- End"
         }
         // Fields are empty, return immediately
        if (emptyErr) {
            alert(errorMsg);
            return;
          }
          //Checks that the input date is after the current time
          function validateDate(minInput, hhInput, ddInput, mmInput,yyyyInput, min, hh, dd, mm,yyyy,name){
                var error = false;
                var errorMsg = "Error "+name+" Date: \n";

                if(yyyyInput<yyyy){
                  errorMsg += "Year is invalid";
                  error = true;
                }
                else if(yyyyInput == yyyy){
                  if (mmInput<mm){
                    errorMsg += "Month is invalid";
                    error = true;
                  }
                  else if(mmInput == mm){
                      if(ddInput<dd){
                        errorMsg += "Day is invalid";
                        error = true;
                      }
                      else if(ddInput==dd){
                          if(hhInput<hh){
                            errorMsg += "hour is invalid";
                            error = true;
                          }
                          else if(hhInput==hh){
                            if(minInput <= min){
                              errorMsg += "Minute is invalid";
                              error = true;
                            }
                          }
                      }
                      
                  }
                }

                if(error){
                  errorMsg = "Error: " + name + " Date must be in the future.";
                  alert(errorMsg);
                  return false;
                }
                
                return true;
          }

          //Parses the html date
          function parseDate(start){
              var inputDate=start.split("-");
              var yyyyInput = parseInt(inputDate[0]);
              var mmInput = parseInt(inputDate[1]);
              var ddInput = parseInt(inputDate[2]);         

              inputDate=start.split("-");
              var yyyyInput = parseInt(inputDate[0]);
              var mmInput = parseInt(inputDate[1]);
              var ddInput = parseInt(inputDate[2]);
//              alert("YYY: "+yyyyInput);
 //             alert("mm: "+mmInput);
 //             alert("dd: "+ddInput);

              inputTime = start.split("T");
              var time = inputTime[1];
              //alert("time: "+time);
              hourMin = time.split(":");
              var hhInput = parseInt(hourMin[0]);
              var minInput = parseInt(hourMin[1]);
 //             alert(hhInput);
 //             alert(minInput);

              var result = new Array();
              result[0] = minInput;
              result[1] = hhInput;
              result[2] = ddInput;
              result[3] = mmInput;
              result[4] = yyyyInput;

              return result;
          }

          //Get the current date

          var today = new Date();
          var dd = today.getDate();
          var mm = today.getMonth()+1;
          var yyyy = today.getFullYear();
          var hours = today.getHours();
          var minutes = today.getMinutes();

          var result1 = parseDate(start);
          //alert("result1: "+ result1+"|"+minutes+" "+hours+" "+dd+" "+mm+" "+yyyy);

          var result2 = parseDate(end);
          //alert("result2: "+ result2+"|"+minutes+" "+hours+" "+dd+" "+mm+" "+yyyy);

          
          if(validateDate(result1[0],result1[1],result1[2],result1[3],result1[4],minutes,
                          hours,dd,mm,yyyy,"Start") == false){
             return;
          }

          if(validateDate(result2[0],result2[1],result2[2],result2[3],result2[4],minutes,
                          hours,dd,mm,yyyy,"End") == false){
             return;
          }

          if(validateDate(result2[0],result2[1],result2[2],result2[3],result2[4],
                        result1[0],result1[1],result1[2],result1[3],
                        result1[4],"End date cannot be before start. ") == false){
             return;
          }
          


        // Use ajax to post to server and update document
        $.ajax({
            type: "POST",
            url: "createEvent",
            data: allJSON,
            dataType: 'json',
            success: function(response_data){
                window.location.replace(response_data['redirect']);
            },
            error: function(data){
            }
        });

    });

});