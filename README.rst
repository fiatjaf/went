**went** stands for *webmention endpoint tools*.

    import went
    webmention = went.Webmention(source_url, target=target_url)
    webmention = went.Webmention(source_html, target=target_url)

    webmention.date == '2015-02-26'
    webmention.url == 'http://someone.com/blog/hello.html'
    webmention.name == 'Hello'
    webmention.body == '<p>Hello!</p>'
    webmention.via == 'twitter.com' # bridgy-specific
    webmention.author['name'] == 'Someone'
    webmention.author['url'] == 'http://someone.com/'
    webmention.author['photo'] == 'http://someone.com/photo.jpg'
