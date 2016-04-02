(function(){
  
  function SearchBar(){
    var self = this;
    
    
    var input;
    var getter = function(){return [];};
    var filter = new Function();
    
    
    self.getter = Getter;
    self.filter = Filter;
    
    
    function Getter(_getter){
      getter = _getter;
    }
    function Filter(_filter){
      filter = _filter;
    }
    
    
    function Update(){
      var list = getter();
      for(var i=0; i<list.length; i++){
        var value = list[i];
        filter(input.value, value);
      }
    }
    
    
    (function(_elem){
      input = _elem;
      
      input.addEventListener('keypress', Update);
      input.addEventListener('keyup', Update);
    }).apply(self, arguments);
  }
  
  window.SearchBar = SearchBar;
  
})();