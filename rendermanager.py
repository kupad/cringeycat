from staticjinja import Site

def render(user, follows):
    print("rendering: ", user)
    context = {'follows': follows}
    site = Site.make_site(
        env_globals=context,
        outpath=f"build/{user}",
    )
    
    site.render(
        use_reloader=False
    )

