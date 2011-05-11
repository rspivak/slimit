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

         'if(elem&&elem.parentNode){if(elem.id!==match[2]){return rootjQuery.find(selector);}this.length=1;this[0]=elem;}'
         ),

        ("""
        var a = function( obj ) {
                for ( var name in obj ) {
                        return false;
                }
                return true;
        };
        """,
         'var a=function(obj){for(var name in obj){return false;}return true;};'
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

        ("""
        delete x;
        typeof x;
        void x;
        x += (!y)++;

        label: while (i <= 7) {
          if ( i == 3 )
              continue;
          if ( i == 0 )
              continue label;
          switch (day) {
            case 5:
                x = 'Friday';
                break ;
            default:
                break label;
          }
        }
        """,

         "delete x;typeof x;void x;x+=(!y)++;label:while(i<=7){if(i==3)continue;if(i==0)continue label;switch(day){case 5:x='Friday';break;default:break label;}}"
         ),

        ("""
        do { x += 1; } while(true);

        var a = [1, 2, 3, ,,,5];

        with (obj) {
          a = b;
        }


        function a(x, y) {
         var re = /ab+c/;
         if (x == 1)
           return x + y;
         if (x == 3)
           return {x: 1};
         else
           return;
        }

        try {
          throw "myException"; // generates an exception
        }
        catch (e) {
          // statements to handle any exceptions
          logMyErrors(e); // pass exception object to error handler
        }
        finally {
          closeMyFile(); // always close the resource
        }
        """,
         'do{x+=1;}while(true);var a=[1,2,3,,,,5];with(obj){a=b;}function a(x,y){var re=/ab+c/;if(x==1)return x+y;if(x==3)return{x:1};else return;}try {throw "myException";} catch(e){logMyErrors(e);} finally {closeMyFile();}'
         ),

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

        ]


def make_test_function(input, expected):

    def test_func(self):
        self.assertMinified(input, expected)

    return test_func

for index, (input, expected) in enumerate(MinifierTestCase.TEST_CASES):
    func = make_test_function(input, expected)
    setattr(MinifierTestCase, 'test_case_%d' % index, func)
