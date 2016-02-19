function Favorite(element, picid, username) {
  this.element = element;
  this.picid = picid;
  // element.value = "hello";
  element.value = username; // objects in Javascript are assigned by reference, so this works
  element.addEventListener("click", this, false); 
}

Favorite.prototype.handleEvent = function(e) {
  if (e.type === "click") {
    // this.update(this.picid, this.element.value);
    this.update(this.picid, this.element);
  }
}

//value is an object with id=picid, num_favorites=0, latest_favorite=""
Favorite.prototype.change = function(value) {
  console.log(value);
  this.data = value;
  document.getElementById("last_favorite").innerHTML = value.latest_favorite;
  document.getElementById("num_fav").innerHTML = value.num_favorites;
}

Favorite.prototype.update = function(username) {
  makeFavoritePostRequest(this.picid, this.element.value, function() {
    console.log('POST successful.');
  });
}

//GET - GOOD
function makeFavoriteRequest(picid, username, cb) {
  console.log("GET Request for: " + picid);
  qwest.get('/olvk4/pa3/pic/favorites?id=' + picid)
    .then(function(xhr, resp) {
      cb(resp);
    });
}

//POST - SEEMS GOOD
function makeFavoritePostRequest(picid, username, cb) {
  var post_data = {
    'id': picid,
    'username': username,
  };
  var prev_num = document.getElementById("num_fav").innerHTML;
  var num = parseInt(prev_num) + 1;

  document.getElementById("fav").innerHTML = "Favorited!";
  document.getElementById("last_favorite").innerHTML = username;
  document.getElementById("num_fav").innerHTML = num;
  document.getElementById("fav").disabled = true;
  qwest.post('/olvk4/pa3/pic/favorites', post_data, {
    dataType: 'json',
    responseType: 'json'
  }).then(function(xhr, resp) {
    cb(resp);
  });
}

function initFavorite(picid, username) {
  var favorites = document.getElementById("fav");
  var favoritesBinding = new Favorite(favorites, picid, username);


  makeFavoriteRequest(picid, username, function(resp) {
    favoritesBinding.change(resp);
    // favoriteBinding.change(resp['fav']);
  });

  setInterval(function() {
   makeFavoriteRequest(picid, username, function(resp) {
      favoritesBinding.change(resp);
      // favoriteBinding.change(resp['fav']);
    }); 
  }, 10000);
}

function update_fav() {
  document.getElementById("fav").innerHTML = "Favorited!";
  document.getElementById("fav").disabled = true;
}
