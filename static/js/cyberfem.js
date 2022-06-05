 
var base_host = window.location.hostname;
let menu = document.getElementById('menu');
var external_links = document.querySelectorAll('.external_links a')
var right_content = document.querySelector('#right_content');
var left_content = document.querySelector('.left_content');
var body = document.getElementsByTagName('BODY')[0];
var select = document.getElementById('menu');
var download_btn = document.getElementById('download_btn');

var index_json;
var index_img_json;
let session_trail_array = JSON.parse(sessionStorage.getItem("trail"));
var pdf_link = "https://cyberfem-pdf-renderer.herokuapp.com/api/render?emulateScreenMedia=false&url="

window.addEventListener('DOMContentLoaded', (event) => {
  document.getElementById("main_content").classList.remove("green-blur");
});


function closeSplash() {
    console.log("close")
    $("#splashPage").hide();
}

function openSplash() {
    console.log("open!")
    $("#index_list").addClass("loading");
    $(".arrows").addClass("loading");
    $(".index_content").addClass("transparent");
    $('#sorting_text').show()
    document.getElementById('index_list').style.pointerEvents = 'none';
}


console.log("hello!!")

function handleMenu(id, elm) {
    str = elm.value
    str = str.toLowerCase();
    if (str == "cyberfeminism index") {
        window.location = base_url + "/"
    } else {
        window.location = base_url + "/" + str;
    }
}

function getUrl() {
    //set menu to url
    var pathArray = window.location.pathname.split('/');
    var secondLevelLocation = pathArray[1];
    var selected_tag = pathArray[2];
    str = secondLevelLocation;
    switch(secondLevelLocation) {
      case "":
        menu.value = "cyberfeminism index";
        var pathHash_array = window.location.hash.split('/');
        var pathHash = pathHash_array[1];
        internal_reference(pathHash)
        scroll_green()
        break;
      case "orderby":
        menu.value = "cyberfeminism index";
        break;
      case "tag":
        menu.value = "cyberfeminism index";
        add_tag_button(selected_tag)
        break;
      case "about":
        menu.value = str;
        var selected_drawer = document.getElementById("about_pg_content")
        internal_ligatures(selected_drawer)
        break;
      case "collections":
        menu.value = str;
        let curator_list = document.getElementsByName('collection');
        if (selected_tag) {
            for(var i = 0; i < curator_list.length; i++) {
               if(curator_list[i].value == selected_tag)
                   curator_list[i].checked = true;
             }
        }
        break;
      case "pdf":
        right_content.classList.add("unopened");
        break;
      default:
        menu.value = str;
    }

    // force all external links only to be target=_blank
    for (var links = external_links, i = 0, a; a = links[i]; i++) {
        if (a.host !== location.host) {
            a.target = '_blank';
        }
    }
}


function sort_loading(order) {
    $("#index_list").addClass("loading");
    $(".arrows").addClass("loading");
    $(".index_content").addClass("transparent");
    $('#sorting_text').show()
    document.getElementById('index_list').style.pointerEvents = 'none';

    window.location = base_url+"/orderby/"+ order
    setTimeout(function() {
        $("#index_list").addClass("loading2");
        $(".arrows").addClass("loading2");
    }, 400);
    setTimeout(function() {
        $("#index_list").removeClass("loading2")
        $(".arrows").removeClass("loading2");
        $("#index_list").addClass("loading3");
        $(".arrows").addClass("loading3");
    }, 800);
    setTimeout(function() {
        $("#index_list").removeClass("loading3")
        $(".arrows").removeClass("loading3");
        $("#index_list").addClass("loading4");
        $(".arrows").addClass("loading4");
    }, 1200);
    setTimeout(function() {
        $("#index_list").removeClass("loading4")
        $(".arrows").removeClass("loading4");
        $(".index_content").removeClass("transparent");
    }, 15000);
}

var download_btn = document.getElementById("download_btn");
var today = new Date();
var dd = String(today.getDate()).padStart(2, '0');
var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
var yyyy = today.getFullYear();
today = yyyy + '-' + mm + '-' + dd;
var trail_array_ids = []

function create_pdf() {
    for (i = 0; i < trail_array.length; i++) {
        let obj = index_json.find(o => o.slug === trail_array[i]);
        trail_array_ids.push(obj.page_ptr_id);
    }
    str = pdf_link + base_url + '/pdf/?page_ptr_id=' + trail_array_ids;
    window.open(str, '_blank');
}

function view_downloads() {
    var viewdownloads_list = document.getElementById("viewdownloads_list");
    var base_index_list = document.getElementById("base_index_list");
    base_index_list.classList.toggle("hide");
    viewdownloads_list.classList.toggle("hide");
}

function remove_trail_entry(elm, slug, title) {
    elm.remove();

    var index_elm = document.getElementById(slug);
    index_elm.classList.remove("green_text");
    index_elm.nextSibling.nextSibling.classList.add("closed")
    
    trail_array = trail_array.filter(e => e !== slug);
    sessionStorage.setItem('trail', JSON.stringify(trail_array));
    download_btn.innerHTML = "download ("+ trail_array.length + ")"

}

var trail_array = [];
var opened = false;
function add_to_trail(slug) {
    table = document.getElementById("base_index_table");
    let obj = index_json.find(o => o.slug === slug);

    if (!trail_array.includes(obj.slug)) {
        trail_array.push(slug);
        var row = table.insertRow(0);
        var cell1 = row.insertCell(0);
        // var cell2 = row.insertCell(1);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);

        cell1.innerHTML = "("+obj.rownum+")";
        cell1.classList.add("cr")

        cell2.innerHTML = obj.title;
        
        if (obj.author_founder == undefined || obj.author_founder == "None") {
            cell3.innerHTML = "";
        } else {
            cell3.innerHTML = obj.author_founder;
        }
        row.classList.add("base_tr")
        row.setAttribute("id", obj.slug + "_base");
        row.setAttribute("title", obj.title);
        row.addEventListener("click",  function(){ remove_trail_entry(this, slug); });
        table.appendChild(row);  
    }

    // open left_content drawer
    if (trail_array.length == 1 && opened == false &&  window.innerWidth > 800) {
        opened = true;
        right_content.classList.toggle("unopened");
        left_content.style.width = "73.5%";
    }
    if (trail_array.length == 1 && opened == false &&  window.innerWidth < 800) {
        right_content.style.display = "none";
    }

    download_btn.innerHTML = "download ("+ trail_array.length + ")";
    // console.log("added to trail")
    sessionStorage.setItem('trail', JSON.stringify(trail_array));
}

function session_trail(){
    if (session_trail_array) {
        for (i = 0; i < session_trail_array.length; i++) {
            let obj = index_json.find(o => o.slug === session_trail_array[i]);
            add_to_trail(obj.slug)        }
        opened = true;
        right_content.classList.remove("unopened");
        left_content.style.width = "73.5%";
    }
}

function internal_reference(id) {
    if (id) {
        var e = document.getElementById(id);
        e.scrollIntoView({behavior: "smooth", block: "center", inline: "nearest"});
        slideIndex_drawer(e, id)
    }
}

function internal_ligatures(selected_drawer) {
    // internal links
    if(menu.value == "cyberfeminism index" || menu.value == "search" || menu.value == "collections") {
        var n = []
        var node = selected_drawer.children[0].children
        // console.log(node)
        for (i = 0; i < node.length; i++) { 
            for (j = 0; j < node[i].children.length; j++) {
                if (node[i].children[j].nodeName == "EM") {
                    for (k = 0; k < node[i].children[j].childNodes.length; k++) {
                        if (node[i].children[j].childNodes[k].nodeName == "A" && node[i].children[j].childNodes[k].innerHTML == "(x)") {
                            n.push(node[i].children[j].childNodes[k])
                        }
                    } 
                }
                if (node[i].children[j].nodeName == "A" && node[i].children[j].innerHTML == "(x)") {
                    n.push(node[i].children[j])
                } 
                if (node[i].children[j].nodeName == "A" && node[i].children[j].innerHTML != "(x)") {
                    node[i].children[j].target = '_blank';
                }
            }
        }
    } 
    if(menu.value == "images") {
        var node = selected_drawer.children[0].children[4];
        var n = node.children
    }
    if(menu.value == "about") {
        var n = []
        var node = selected_drawer.children;
        // console.log(node)
        for (i = 0; i < node.length; i++) { 
            for (j = 0; j < node[i].children.length; j++) {
                if (node[i].children[j].nodeName == "EM") {
                    for (k = 0; k < node[i].children[j].childNodes.length; k++) {
                        if (node[i].children[j].childNodes[k].nodeName == "A" && node[i].children[j].childNodes[k].innerHTML == "(x)") {
                            n.push(node[i].children[j].childNodes[k])
                        }
                    } 
                }
                if (node[i].children[j].nodeName == "A" && node[i].children[j].innerHTML == "(x)") {
                    n.push(node[i].children[j])
                } 
                if (node[i].children[j].nodeName == "A" && node[i].children[j].innerHTML != "(x)") {
                    node[i].children[j].target = '_blank';
                }
            }
        }
        // console.log(n)
    }

    if (node.classList != "external_links") {
        for (i = 0; i < n.length; i++) { 
            console.log("here")
            console.log(n)
            if(n[i] && n[i].nodeName == "A" && n[i].text == "(x)") {
                var inline_link = n[i].href
                var parts = inline_link.split('/');
                var entry_slug = parts[parts.length - 2];
                n[i].href= base_url +"/#/" + entry_slug
                let obj = index_json.find(o => o.slug === decodeURIComponent(entry_slug));

                n[i].innerHTML = "<span slug='"+obj.slug+"' title='"+obj.title+"' class='tooltip'>("+ obj.rownum + ")</span>";

                n[i].classList.add("cr")
                n[i].setAttribute("slug", entry_slug)

                if(menu.value == "about") {
                    n[i].addEventListener("click", function(e){
                        return internal_reference(e.srcElement.attributes[0].nodeValue)
                    });
                } else {
                    n[i].addEventListener("click", function(e){
                        add_to_trail(obj.slug)
                        return internal_reference(e.srcElement.attributes[0].nodeValue)
                    });
                }
            }
        }
    }
}

function slideIndex_drawer(elm, url) {
    var selected_drawer = elm.nextSibling.nextSibling;

    if (elm.classList.contains("green_text")) {
        elm.classList.remove("green_text")
        if (selected_drawer.classList.contains("closed")) {
        } else {
            selected_drawer.classList.add("closed")
        }
    } else {
        elm.classList.add("green_text")
        selected_drawer.classList.remove("closed")
    }
    var hist_str = "#/" + url
    window.history.pushState(hist_str, 'Title', hist_str);

    internal_ligatures(selected_drawer)
}

function slideIndex_drawer_images(elm, url) {
    var elems = document.querySelectorAll(".index_drawer");
    var elem_entry = document.querySelectorAll(".index_entry");
    var selected_drawer = elm.previousSibling.previousSibling;

    [].forEach.call(elems, function(el) {
        if (el.classList.contains('closed')) {
        } else {
            el.classList.add("closed");
            e_index_entry = el.nextElementSibling
            images = e_index_entry.querySelectorAll(".img_container img");
        }
    });
    

    elm.classList.add("green_text");
    selected_drawer.classList.toggle('closed');

    var hist_str = "#/" + url;
    window.history.pushState(hist_str, 'Title', hist_str);

    elm.scrollIntoView({behavior: "smooth", block: "center", inline: "nearest"});

    internal_ligatures(selected_drawer)
}


function back_to_top(id) {
    var e = document.getElementById(id);
    e.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
}

function add_tag_button(selected_tag) {
    var elem = document.createElement("button");
    elem.innerHTML = "<span>x</span> " + selected_tag;

    elem.onclick = function() { // Note this is a function
        tagbtns.remove();
        window.location = base_url+"/";
    };
    var tagbtns = document.getElementById("tag_btn");
    tagbtns.appendChild(elem);
    menu = document.getElementById('menu');
    menu.classList.add("with_tag")

    var position_info = tagbtns.getBoundingClientRect();
    var position_width = position_info.width;
    var width_menu = menu.getBoundingClientRect().width;
    var s = width_menu - position_width - 10;
    menu.style.width = s+"px"
}

function enlarge_img(el) {
    if (el.classList.contains('enlarge_img')) {
        el.classList.remove("enlarge_img");
        caption = el.nextElementSibling.nextElementSibling
        caption.style.display = "none";
    } else {
        el.classList.add("enlarge_img")
        img_width = el.offsetWidth
        if(img_width > 250) {
            el.style.height = "auto";
            // img_container = el.parentElement;
            // img_container.style.display = "block";
        }
        caption = el.nextElementSibling.nextElementSibling
        caption.style.display = "block";
        caption.style.color = "black";
        caption.style.width = img_width+"px";
    }
}

function img_click(url) {
    var id = "base"+url
    var e = document.getElementById(id);
    var s = document.getElementById("right_content");

    var elems = document.querySelectorAll(".base_tr");
    [].forEach.call(elems, function(el) {
        if (el.classList.contains('green_text')) {
            el.classList.remove("green_text");
        }
    })

    e.classList.add("green_text");

    e.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' })
}


function scroll_green() {
    var index_list = document.getElementById("left_index");
    var scrollpos = index_list.scrollTop;
    var green_box = document.getElementById("green_box");

    index_list.addEventListener('scroll', function(){ 
        
        scrollpos = index_list.scrollTop;

        if(scrollpos < 100){
           green_box.classList.remove("extend_green", "extend_green_two", "extend_green_three");
        }
        else if(scrollpos >= 100 && scrollpos < 200) {
          green_box.classList.add("extend_green");
          green_box.classList.remove("extend_green_two", "extend_green_three");
        }
        else if(scrollpos >= 200 && scrollpos < 300) {
          green_box.classList.add("extend_green_two");
          green_box.classList.remove("extend_green_one", "extend_green_three");
        }
        else {
          green_box.classList.add("extend_green_three");
          green_box.classList.remove("extend_green_one", "extend_green_two");
        }
    });

    // Setup isScrolling variable
    var isScrolling;
    index_list.addEventListener('scroll', function ( event ) {
        window.clearTimeout( isScrolling );
        isScrolling = setTimeout(function() {
        green_box.classList.remove("extend_green", "extend_green_two", "extend_green_three");
        }, 1000);
    }, false);
}

function search_url(cat_name) {
    window.location = base_url+"/tag/"+ cat_name;
}

function collection_url(col_name) {
    window.location = base_url+"/collections/"+ col_name;
}

// on start calls
getUrl()
session_trail()
openSplash()