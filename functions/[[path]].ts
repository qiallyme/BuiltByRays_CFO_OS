export const onRequestGet: PagesFunction = async (ctx) => {
    const res = await ctx.next();           // try the static asset first
    if (res.status !== 404) return res;     // if found, serve it
    return ctx.env.ASSETS.fetch(new URL("/index.html", ctx.request.url)); // else SPA fallback
  };
  