'use strict';
(function (root) {
  
  function DocContent () {
    this.init();
  }
  
  DocContent.prototype = {
    init: function () {
      // Cache all the elements first on the instance
      this.$content = $('.js-DocFrame');
      this.$methodLabel = $('.js-Method', this.$content);
      this.$pathLabel = $('.js-Path', this.$content);
      this.$parameters = $('.js-DocParameters', this.$content);
      
      this.bindEvents();
    },
    bindEvents: function () {
      
    },
    render: function (route) {
      this.renderHeader(route);
      this.renderParameters(route);
    },
    renderHeader: function (route) {
      this.$methodLabel.innerHTML = route.methods[0];
      
      var path = route.path.replace(/^\/api\/v{{ version }}/, '');
      path = path.replace(/\:([^/]+)/g, '<div class="UrlParameter">$1</div>');
      this.$pathLabel.innerHTML = path;
    },
    renderParameters: function (route) {
      this.$parameters.innerHTML = '';
      this.renderDocString(route);
      this.renderUrlParameters(route);
      this.renderHeaderParameters(route);
      this.renderQueryParameters(route);
      this.renderBodyParameters(route);
    },
    renderParameterDict: function (param_dict, parent, indent) {
      var hasParams = false;
      
      for(var parameter_name in param_dict){
        hasParams = true;
        var parameter = param_dict[parameter_name];
        var row   = $new('div.KeyValueList-Row', parent);
        var key   = $new('div.KeyValueList-Key', row, parameter_name);
        var type  = $new('div.KeyValueList-Value', row, this.typeParser(parameter));
        var attrs = $new('div.KeyValueList-Attributes', row);
        this.attributeParser(parameter.attributes, attrs);
        
        row.style.marginLeft = (10 * indent) + 'px';
        key.style.width = (170 - 10 * indent) + 'px';
        
        if(!!parameter.template){
          if(parameter.type == 'List'){
            this.renderParameterDict({
              '<label style="color:rgb(168,168,168)">List Template</label>': parameter.template
            }, parent, indent + 1);
          }else if(parameter.type == 'Dict'){
            this.renderParameterDict(parameter.template, parent, indent + 1);
          }
        }
        
      }
      
      return hasParams;
    },
    renderParameterSection: function (param_dict, title, header_row) {
      var hasParams = false;
      
      var section = $new('div.EndpointDoc-Section');
      var subtitle = $new('div.EndpointDoc-SubTitle', section, title);
      
      var list = $new('div.KeyValueList', section);
      
      var row   = $new('div.KeyValueList-Row.header', list);
      var key   = $new('div.KeyValueList-Key', row, header_row[0]);
      var type  = $new('div.KeyValueList-Value', row, header_row[1]);
      var attrs = $new('div.KeyValueList-Attributes', row, header_row[2]);
      
      var hasParams = this.renderParameterDict(param_dict, list, 0);
      if (hasParams)
        this.$parameters.appendChild(section);
    },
    renderUrlParameters: function (route) {
      this.renderParameterSection(
        route.url, 'URL Parameters',
        ['URL Parameter', 'Type', 'Attributes']
      );
    },
    renderQueryParameters: function (route) {
      this.renderParameterSection(
        route.query, 'Query String Parameters',
        ['Query Parameter', 'Type', 'Attributes']
      );
    },
    renderHeaderParameters: function (route) {
      this.renderParameterSection(
        route.headers, 'Header Parameters',
        ['Header', 'Type', 'Attributes']
      );
    },
    renderBodyParameters: function (route) {
      this.renderParameterSection(
        route.body.template, 'Body Parameters',
        ['Key', 'Type', 'Attributes']
      );
    },
    attributeParser: function (attributes, parent) {
      for(var key in attributes){
        var value = attributes[key];
        switch(key){
          case 'required': output = value ? 'required': 'optional'; break;
          default: output = key + '=' + value;
        }
        $new('div.KeyValueList-Attribute', parent, output);
      }
    },
    typeParser: function (parameter) {
      var type = parameter.type;
      if (type == 'Model')
        return parameter.modelname + ' Entity Key';
      return type;
    },
    renderDocString: function (route) {
      var docstring = route.docstring;
      if(!docstring) return;
      
      var section = $new('div.EndpointDoc-Section', this.$parameters);
      var subtitle = $new('div.EndpointDoc-SubTitle', section, 'Summary');
      var summary = $new('div.EndpointDoc-DocString', section, docstring);
    }
  };
  
  root.DocContent = DocContent;
  
})(window);