'use strict';
(function (root) {
  
  function RemoveClass(cls, elem){
    if (!HasClass(cls, elem)) return false;
    var currentClass = elem.getAttribute('class');
    var classList = currentClass.split(' ');
    var index = classList.indexOf(cls);
    classList.splice(index, 1);
    var newClass = classList.join(' ');
    elem.setAttribute('class', newClass);
    return true;
  }
  function AddClass(cls, elem){
    if (HasClass(cls, elem)) return false;
    var currentClass = elem.getAttribute('class');
    elem.setAttribute('class', currentClass + ' ' + cls);
    return true;
  }
  function ToggleClass(cls, elem){
    if (HasClass(cls, elem)) RemoveClass(cls, elem);
    else AddClass(cls, elem);
  }
  function HasClass(cls, elem){
    var currentClass = elem.getAttribute('class');
    var classList = currentClass.split(' ');
    return classList.indexOf(cls) > -1;
  }
  
  root.classes  = {
    remove: RemoveClass,
    add   : AddClass,
    toggle: ToggleClass,
    has   : HasClass
  };

})(window);