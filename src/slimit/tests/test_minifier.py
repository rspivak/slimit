###############################################################################
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import unittest

from slimit import minify


class MinifierTestCase(unittest.TestCase):

    def assertMinified(self, source, expected):
        minified = minify(source)
        self.maxDiff = None
        self.assertSequenceEqual(minified, expected)

    TEST_CASES = [
        ("""
        jQuery.fn = jQuery.prototype = {
                // For internal use only.
                _data: function( elem, name, data ) {
                        return jQuery.data( elem, name, data, true );
                }
        };
        """,
         'jQuery.fn=jQuery.prototype={_data:function(elem,name,data){return jQuery.data(elem,name,data,true);}};'),

        ('context = context instanceof jQuery ? context[0] : context;',
         'context=context instanceof jQuery?context[0]:context;'
         ),

        ("""
        /*
        * A number of helper functions used for managing events.
        * Many of the ideas behind this code originated from
        * Dean Edwards' addEvent library.
        */
        if ( elem && elem.parentNode ) {
                // Handle the case where IE and Opera return items
                // by name instead of ID
                if ( elem.id !== match[2] ) {
                        return rootjQuery.find( selector );
                }

                // Otherwise, we inject the element directly into the jQuery object
                this.length = 1;
                this[0] = elem;
        }
        """,

         'if(elem&&elem.parentNode){if(elem.id!==match[2])return rootjQuery.find(selector);this.length=1;this[0]=elem;}'
         ),

        ("""
        var a = function( obj ) {
                for ( var name in obj ) {
                        return false;
                }
                return true;
        };
        """,
         'var a=function(obj){for(var name in obj)return false;return true;};'
         ),

        ("""
        x = "string", y = 5;

        (x = 5) ? true : false;

        for (p in obj)
        ;

        if (true)
          val = null;
        else
          val = false;

        """,
         'x="string",y=5;(x=5)?true:false;for(p in obj);if(true)val=null;else val=false;'
         ),

        # for loops + empty statement in loop body
        ("""
        for (x = 0; true; x++)
        ;
        for (; true; x++)
        ;
        for (x = 0, y = 5; true; x++)
        ;

        y = (x + 5) * 20;

        """,
         'for(x=0;true;x++);for(;true;x++);for(x=0,y=5;true;x++);y=(x+5)*20;'),


        # unary expressions
        ("""
        delete x;
        typeof x;
        void x;
        x += (!y)++;
        """,
         'delete x;typeof x;void x;x+=(!y)++;'),

        # label + break label + continue label
        ("""
        label:
        if ( i == 0 )
          continue label;
        switch (day) {
        case 5:
          break ;
        default:
          break label;
        }
        """,
         'label:if(i==0)continue label;switch(day){case 5:break;default:break label;}'),

        # break + continue: no labels
        ("""
        while (i <= 7) {
          if ( i == 3 )
              continue;
          if ( i == 0 )
              break;
        }
        """,
         'while(i<=7){if(i==3)continue;if(i==0)break;}'),

        # regex + one line statements in if and if .. else
        ("""
        function a(x, y) {
         var re = /ab+c/;
         if (x == 1)
           return x + y;
         if (x == 3)
           return {x: 1};
         else
           return;
        }
        """,
         'function a(x,y){var re=/ab+c/;if(x==1)return x+y;if(x==3)return{x:1};else return;}'),

        # new
        ('return new jQuery.fn.init( selector, context, rootjQuery );',
         'return new jQuery.fn.init(selector,context,rootjQuery);'
         ),

        # no space after 'else' when the next token is (, {
        ("""
        if (true) {
          x = true;
          y = 3;
        } else {
          x = false
          y = 5
        }
        """,
         'if(true){x=true;y=3;}else{x=false;y=5;}'),

        ("""
        if (true) {
          x = true;
          y = 3;
        } else
          (x + ' qw').split(' ');
        """,
         "if(true){x=true;y=3;}else(x+' qw').split(' ');"),


        ##############################################################
        # Block braces removal
        ##############################################################

        # do while
        ('do { x += 1; } while(true);', 'do x+=1;while(true);'),
        # do while: multiple statements
        ('do { x += 1; y += 1;} while(true);', 'do{x+=1;y+=1;}while(true);'),

        # elision
        ('var a = [1, 2, 3, ,,,5];', 'var a=[1,2,3,,,,5];'),

        # with
        ("""
        with (obj) {
          a = b;
        }
        """,
         'with(obj)a=b;'),

        # with: multiple statements
        ("""
        with (obj) {
          a = b;
          c = d;
        }
        """,
         'with(obj){a=b;c=d;}'),

        # if else
        ("""
        if (true) {
          x = true;
        } else {
          x = false
        }
        """,
         'if(true)x=true;else x=false;'),

        # if: multiple statements
        ("""
        if (true) {
          x = true;
          y = false;
        } else {
          x = false;
          y = true;
        }
        """,
         'if(true){x=true;y=false;}else{x=false;y=true;}'),

        # try catch finally: one statement
        ("""
        try {
          throw "my_exception"; // generates an exception
        }
        catch (e) {
          // statements to handle any exceptions
          log(e); // pass exception object to error handler
        }
        finally {
          closefiles(); // always close the resource
        }
        """,
         'try{throw "my_exception";}catch(e){log(e);}finally{closefiles();}'
         ),

        # try catch finally: no statements
        ("""
        try {
        }
        catch (e) {
        }
        finally {
        }
        """,
         'try{}catch(e){}finally{}'
         ),

        # try catch finally: multiple statements
        ("""
        try {
          x = 3;
          y = 5;
        }
        catch (e) {
          log(e);
          log('e');
        }
        finally {
          z = 7;
          log('z');
        }
        """,
         "try{x=3;y=5;}catch(e){log(e);log('e');}finally{z=7;log('z');}"
         ),

        # tricky case with an 'if' nested in 'if .. else'
        # We need to preserve braces in the first 'if' otherwise
        # 'else' might get associated with nested 'if' instead
        ("""
        if ( obj ) {
                for ( n in obj ) {
                        if ( v === false) {
                                break;
                        }
                }
        } else {
                for ( ; i < l; ) {
                        if ( nv === false ) {
                                break;
                        }
                }
        }
        """,
         'if(obj){for(n in obj)if(v===false)break;}else for(;i<l;)if(nv===false)break;'),

        # We don't care about nested 'if' when enclosing 'if' block
        # contains multiple statements because braces won't be removed
        # by visit_Block when there are multiple statements in the block
        ("""
        if ( obj ) {
                for ( n in obj ) {
                        if ( v === false) {
                                break;
                        }
                }
                x = 5;
        } else {
                for ( ; i < l; ) {
                        if ( nv === false ) {
                                break;
                        }
                }
        }
        """,
         'if(obj){for(n in obj)if(v===false)break;x=5;}else for(;i<l;)if(nv===false)break;'),


        # No dangling 'else' - remove braces
        ("""
        if ( obj ) {
                for ( n in obj ) {
                        if ( v === false) {
                                break;
                        } else {
                                n = 3;
                        }
                }
        } else {
                for ( ; i < l; ) {
                        if ( nv === false ) {
                                break;
                        }
                }
        }
        """,
         'if(obj)for(n in obj)if(v===false)break;else n=3;else for(;i<l;)if(nv===false)break;'),

        # foo["bar"] --> foo.bar
        ('foo["bar"];', 'foo.bar;'),
        ("foo['bar'];", 'foo.bar;'),
        ("""foo['bar"']=42;""", """foo['bar"']=42;"""),
        ("""foo["bar'"]=42;""", """foo["bar'"]=42;"""),
        ('foo["bar bar"];', 'foo["bar bar"];'),
        ('foo["bar"+"bar"];', 'foo["bar"+"bar"];'),
        # https://github.com/rspivak/slimit/issues/34
        # test some reserved keywords
        ('foo["for"];', 'foo["for"];'),
        ('foo["class"];', 'foo["class"];'),


        # https://github.com/rspivak/slimit/issues/21
        # c||(c=393,a=323,b=2321); --> c||c=393,a=323,b=2321; ERROR
        ('c||(c=393);', 'c||(c=393);'),
        ('c||(c=393,a=323,b=2321);', 'c||(c=393,a=323,b=2321);'),

        # https://github.com/rspivak/slimit/issues/25
        ('for(a?b:c;d;)e=1;', 'for(a?b:c;d;)e=1;'),

        # https://github.com/rspivak/slimit/issues/26
        ('"begin"+ ++a+"end";', '"begin"+ ++a+"end";'),

        # https://github.com/rspivak/slimit/issues/28
        ("""
         (function($) {
             $.hello = 'world';
         }(jQuery));
         """,
         "(function($){$.hello='world';}(jQuery));"),

        # function call in FOR init
        ('for(o(); i < 3; i++) {}', 'for(o();i<3;i++){}'),

        # unary increment operator in FOR init
        ('for(i++; i < 3; i++) {}', 'for(i++;i<3;i++){}'),

        # unary decrement operator in FOR init
        ('for(i--; i < 3; i++) {}', 'for(i--;i<3;i++){}'),

        # issue-37, simple identifier in FOR init
        ('for(i; i < 3; i++) {}', 'for(i;i<3;i++){}'),

        # https://github.com/rspivak/slimit/issues/32
        ("""
         Name.prototype = {
           getPageProp: function Page_getPageProp(key) {
             return this.pageDict.get(key);
           },

           get fullName() {
             return this.first + " " + this.last;
           },

           set fullName(name) {
             var names = name.split(" ");
             this.first = names[0];
             this.last = names[1];
           }
         };
         """,
         ('Name.prototype={getPageProp:function Page_getPageProp(key){'
          'return this.pageDict.get(key);},'
          'get fullName(){return this.first+" "+this.last;},'
          'set fullName(name){var names=name.split(" ");this.first=names[0];'
          'this.last=names[1];}};')
        ),
        ]


def make_test_function(input, expected):

    def test_func(self):
        self.assertMinified(input, expected)

    return test_func

for index, (input, expected) in enumerate(MinifierTestCase.TEST_CASES):
    func = make_test_function(input, expected)
    setattr(MinifierTestCase, 'test_case_%d' % index, func)
