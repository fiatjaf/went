**went** stands for *webmention endpoint tools*.

.. code-block:: python

    import went
    webmention = went.Webmention(source_url, target=target_url)
    webmention = went.Webmention(source_html, target=target_url)

    webmention.date == '2015-02-26'
    webmention.url == 'http://someone.com/blog/hello.html'
    webmention.name == 'Hello world'
    webmention.html == '<a href="http://otherpage.com/">to see my <i>hello world</i> go to this other page</a>'
    webmention.body == '[to see my _hello world_ go to this other page](http://otherpage.com/)'
    webmention.via == 'twitter.com' # bridgy-specific
    webmention.author['name'] == 'Someone'
    webmention.author['url'] == 'http://someone.com/'
    webmention.author['photo'] == 'http://someone.com/photo.jpg'
