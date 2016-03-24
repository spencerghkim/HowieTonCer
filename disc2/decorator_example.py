#returns function that prints text in caps
def caps_decorator(f):
    
    def new_f(s):
        s = s.upper()
        return f(s)

    return new_f

#returns function that prints text in bold
def bold_decorator(f):
    
    def new_f(s):
        s = "<b>{0}</b>".format(s)
        return f(s)
    
    return new_f

#decorator syntax
@bold_decorator
def print_bold_html(s):
    return "<p>{0}</p>".format(s)

@caps_decorator
def print_caps_html(s):
    return "<p>{0}</p>".format(s)


#combine multiple decorators
@bold_decorator
@caps_decorator
def print_bold_caps_html(s):
    return "<p>{0}</p>".format(s)


def print_html(s):
    return "<p>{0}</p>".format(s)



if __name__ == "__main__":
    print print_bold_caps_html("hello world")
    
    print caps_decorator(bold_decorator(print_html))("hello world")

    print "it worked!   ",bold_decorator(caps_decorator(print_html))("hello world") == print_bold_caps_html("hello world")

