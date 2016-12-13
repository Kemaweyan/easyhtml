from html.parser import HTMLParser
from . import dom


class TagStack:

    """
    A stack-baset object to store opened
    tags while reading a document.

    """
    def __init__(self):
        # a list of tags, used as a stack
        self.tags = []
        # the last opened tag
        self.current = None

    def push(self, tag):
        # simple tags can't be opened
        if tag.single:
            return
        # if a tag is not simple
        # append it to the list
        self.tags.append(tag)
        # and save as current
        self.current = tag

    def pop(self):

        """
        Extract a last opened tag from the stack
        and makes previous opened one current.

        """
        self.tags.pop()
        try:
            self.current = self.tags[-1]
        except:
            self.current = None

    def clear(self):

        """
        Removes all tags from the stack.

        """
        self.tags.clear()
        self.current = None

    def __contains__(self, name):

        """
        Checks whether a tag with specified name
        is currently opened.

        """
        # skip the first element because
        # that is not a tag but HTMLDocument object
        for tag in self.tags[1:]:
            if name == tag.tag_name:
                return True
        return False

    @property
    def root(self):

        """
        Returns a root (HTMLDocument) object.

        """
        return self.tags[0]




class DOMParser(HTMLParser):

    """
    Parses HTML document and builds
    DOM structure.

    """
    def __init__(self):
        HTMLParser.__init__(self)
        # create a stack object
        self.stack = TagStack()
        # create a root object
        root = dom.HTMLDocument()
        # push root object to the stack
        self.stack.push(root)

    def handle_starttag(self, name, attrs):

        """
        Processes a start tag such as
        <tag attr="value" ...>

        :name: a name of the tag, type str
        :attrs: attributes of the tag, type a list of tuples

        [(attr1, value1), (attr2, value2)...]

        """
        # create a tag
        tag = dom.HTMLTag(name, attrs)
        # append tag as a child
        # to the current tag
        self.stack.current.append(tag)
        # push the tag to the stack
        # the tag would become current
        # if that is not simple tag
        self.stack.push(tag)

    def handle_endtag(self, name):

        """
        Processes an end tag such as </tag>

        :name: a name of the tag, type str

        """
        # if an HTML document has a valid structure, the end tag is the same
        # with the last opened tag. But if document is invalid, there would be
        # end tags without appropriate start tags or start tags without
        # appropriate end tags. Therefore we close all tags opened after
        # the tag which currently is closing and ignore all end tags if there
        # are no appropriate opened ones. For example, an invalid HTML code:
        # <div>     - open DIV tag
        #   <p>     - open P tag and append it to DIV
        #   </div>  - close P tag and DIV tag
        # </p>      - ignore it
        # so there would be a DIV tag object with a child P tag inside as it's
        # expected if the HTML code were correct.
        if name in self.stack:
            # close all tags until encounter an appropriate one
            while name != self.stack.current.tag_name:
                self.stack.pop()
            # close the tag
            self.stack.pop()

    def handle_data(self, data):

        """
        Process a plain text.

        :data: data of the text, type str

        """
        # ignore empty strings without printable characters
        if not data.strip(' \n\t\xA0'):
            return
        # create a PlainText object
        element = dom.PlainText(data)
        # and append it to current opened tag
        self.stack.current.append(element)

    def handle_entityref(self, name):

        """
        Process a named entity such as &name;

        :name: a name of the entity, type str

        """
        try:
            # create an entity by its name
            element = dom.NamedEntity(name)
        except:
            # if there is no entity with specified name
            # use its code as a palin text
            element = dom.PlainText('&' + name + ';')
        # append result to current opened tag
        self.stack.current.append(element)
        
    def handle_charref(self, num):

        """
        Process a numeric entity such as &name;

        :num: a numeric code of the character, type str

        """
        try:
            # create an entity by its code
            element = dom.NumEntity(num)
        except:
            # if there is no entity with specified name
            # use its code as a palin text
            element = dom.PlainText('&#' + num + ';')
        # append result to current opened tag
        self.stack.current.append(element)
        
    def handle_comment(self, data):

        """
        Process a comment such as <!-- comment -->

        :data: data of the comment, type str

        """
        # create a comment object
        element = dom.HTMLComment(data)
        # append result to current opened tag
        self.stack.current.append(element)

    def handle_decl(self, decl):

        """
        Processes a document declaration
        such as <!DOCTYPE ...>

        :decl: a string of declaration, type str

        """
        self.stack.root.doctype = dom.DoctypeDeclaration(decl)

    def get_dom(self):

        """
        Returns a DOM of the document or None if
        DOM does not exist.

        Prepare the parser for a new document.

        """
        try:
            # get a root elemtn - HTMLDocument object
            dom_root = self.stack.root
        except:
            # HTMLDocument does not exist
            return None
        else:
            # return result
            return dom_root
        finally:
            # clear the stack
            self.stack.clear()
            # and create a new HTMLDocument object
            root = dom.HTMLDocument()
            # append a new root element to the stack
            self.stack.push(root)
