// https://github.com/ghiculescu/jekyll-table-of-contents
(function($){
    
    function Stack(){
        this.dataStore = []
        this.top    = 0;
        this.push   = push
        this.pop    = pop
        this.peek   = peek
        this.length = length;
        this.toc_number = toc_number;
        this.inc_number = inc_number;
    }
    
    function push(element){
        this.dataStore[this.top++] = element;
    }
    
    function peek(element){
        return this.dataStore[this.top-1];
    }
    
    function pop(){
        return this.dataStore[--this.top];
    }
    
    function clear(){
        this.top = 0
    }
    
    function length(){
        return this.top
    }
    
    function toc_number() {
        var num = "";
        for (i = 0; i < this.top; i++) {
            num += this.dataStore[i] + ".";
        }
        return num;
    }
    
    function inc_number() {
        this.dataStore[this.top - 1]++;
    }
    
  $.fn.toc = function(options) {
    var defaults = {
      noBackToTopLinks: false,
      title: 'Table Of Content',
      minimumHeaders: 3,
      headers: 'h1, h2, h3, h4, h5, h6',
      listType: 'ol', // values: [ol|ul]
      showEffect: 'show', // values: [show|slideDown|fadeIn|none]
      showSpeed: 0 // set to 0 to deactivate effect
    },
    settings = $.extend(defaults, options);

    function fixedEncodeURIComponent (str) {
      return encodeURIComponent(str).replace(/[!'()*]/g, function(c) {
        return '%' + c.charCodeAt(0).toString(16);
      });
    }

    var headers = $(settings.headers).filter(function() {
      // get all headers with an ID
      var previousSiblingName = $(this).prev().attr( "name" );
      if (!this.id && previousSiblingName) {
        this.id = $(this).attr( "id", previousSiblingName.replace(/\./g, "-") );
      }
      return this.id;
    }), output = $(this);
    if (!headers.length || headers.length < settings.minimumHeaders || !output.length) {
      $(this).hide();
      return;
    }

    var render = {
      show: function() { output.hide().html(html).show(settings.showSpeed); },
      slideDown: function() { output.hide().html(html).slideDown(settings.showSpeed); },
      fadeIn: function() { output.hide().html(html).fadeIn(settings.showSpeed); },
      none: function() { output.html(html); }
    };

    var get_level = function(ele) { return parseInt(ele.nodeName.replace("H", ""), 10); }
    var highest_level = headers.map(function(_, ele) { return get_level(ele); }).get().sort()[0];
    var return_to_top = '<i class="icon-arrow-up back-to-top"> </i>';
    
    var stack = new Stack();
    stack.push(0);
    var level = get_level(headers[0]),
      this_level,
      html = "<strong class=\"toc-title\">" + settings.title + "</strong>\n";
      html += " <"+settings.listType+" class=\"toc\">";
    headers.on('click', function() {
      if (!settings.noBackToTopLinks) {
        window.location.hash = this.id;
      }
    })
    .addClass('clickable-header')
    .each(function(_, header) {
      this_level = get_level(header);
      if (!settings.noBackToTopLinks && this_level === highest_level) {
        $(header).addClass('top-level-header').after(return_to_top);
      }
      if (this_level === level) {// same level as before; same indenting
        stack.inc_number();
        html += "<li class=\"toc-item toc-level-" + this_level + "\">";
        html += "<a class=\"toc-link\" href='#" + fixedEncodeURIComponent(header.id) + "'>";
        html += "<span class='toc-number'>" + stack.toc_number() + "</span>"
        html += "<span class='toc-text'>" + header.innerHTML + "</span>";
        html += "</a>";
        
      } else if (this_level <= level){ // higher level than before; end parent ol
        for(i = this_level; i < level; i++) {
          stack.pop();
          html += "</li></"+settings.listType+">"
        }
        stack.inc_number();
        html += "<li class='toc-item toc-level-" + this_level + "'><a href='#" + fixedEncodeURIComponent(header.id) + "'>";
        html += "<span class='toc-number'>" + stack.toc_number() + "</span>"
        html += "<span class='toc-text'>" + header.innerHTML + "</span>";
        html += "</a>";
      }
      else if (this_level > level) { // lower level than before; expand the previous to contain a ol
      if (stack.length() > 1) {
          return;
      }
        for(i = this_level; i > level; i--) {
          stack.push(0);
          html += "<"+settings.listType+" class='toc-child'><li class='toc-item toc-level-" + i + "'>"
        }
        stack.inc_number();
        html += "<a href='#" + fixedEncodeURIComponent(header.id) + "'>";
        html += "<span class='toc-number'>" + stack.toc_number() + "</span>"
        html += "<span class='toc-text'>" + header.innerHTML + "</span>";
        html += "</a>";
      }
      level = this_level; // update for the next one
    });
    html += "</"+settings.listType+">";
    if (!settings.noBackToTopLinks) {
      $(document).on('click', '.back-to-top', function() {
        $(window).scrollTop(0);
        window.location.hash = '';
      });
    }

    render[settings.showEffect]();
  };
})(jQuery);

(function(window,document,undefined){
    var hearts = [];
    
    window.requestAnimationFrame = (function(){
        return window.requestAnimationFrame || 
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame ||
         window.oRequestAnimationFrame ||
         window.msRequestAnimationFrame ||
         function (callback){
             setTimeout(callback,1000/60);
         }
    })();
    
    init();

    function init(){
        css(".heart{width: 10px;height: 10px;position: fixed;background: #f00;transform: rotate(45deg);-webkit-transform: rotate(45deg);-moz-transform: rotate(45deg);}.heart:after,.heart:before{content: '';width: inherit;height: inherit;background: inherit;border-radius: 50%;-webkit-border-radius: 50%;-moz-border-radius: 50%;position: absolute;}.heart:after{top: -5px;}.heart:before{left: -5px;}");
        attachEvent();
        gameloop();
    }

    function gameloop(){
        for(var i=0;i<hearts.length;i++){
            if(hearts[i].alpha <=0){
                document.body.removeChild(hearts[i].el);
                hearts.splice(i,1);
                continue;
             }

             hearts[i].y--;
             hearts[i].scale += 0.004;
             hearts[i].alpha -= 0.013;
             hearts[i].el.style.cssText = "left:"+hearts[i].x+"px;top:"+hearts[i].y+"px;opacity:"+hearts[i].alpha+";transform:scale("+hearts[i].scale+","+hearts[i].scale+") rotate(45deg);background:"+hearts[i].color;
        }

        requestAnimationFrame(gameloop);
    }

    function attachEvent(){
        var old = typeof window.onclick==="function" && window.onclick;
        window.onclick = function(event){
            old && old();
            createHeart(event);
        }
    }

    function createHeart(event){
        var d = document.createElement("div");
        d.className = "heart";
        hearts.push({
            el : d,
            x : event.clientX - 5,
            y : event.clientY - 5,
            scale : 1,
            alpha : 1,
            color : randomColor()
        });

        document.body.appendChild(d);
    }

    function css(css){
        var style = document.createElement("style");
        style.type="text/css";
        try{
            style.appendChild(document.createTextNode(css));
        }
        catch(ex){
            style.styleSheet.cssText = css;
        }

        document.getElementsByTagName('head')[0].appendChild(style);
    }

    function randomColor(){
        return "rgb("+(~~(Math.random()*255))+","+(~~(Math.random()*255))+","+(~~(Math.random()*255))+")";
    }
    
})(window,document);