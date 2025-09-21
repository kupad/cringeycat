/*
const TitleMaxlen = 60, TitleMinlen = 24
const TitleTruncRe = new RegExp(`([-,.!;:)]\s[^-,.!;:]{0,${TitleMaxlen - TitleMinlen}}|\\s\\S*)$`)
const TitleTrunc = function(title) {
  if (title.length < TitleMaxlen)
    return title
  let res = title.slice(0, TitleMaxlen).match(TitleTruncRe)
  let index = TitleMaxlen
  if (res != null && res.index > TitleMinlen)
    index = res.index + 1
  return <span>{title.slice(0, index)}<s>{title.slice(index)}</s></span>
}
 */

function toggleShow(e, parentSel, cls) {
  e.preventDefault()
  const el = e.target;
  el.closest(parentSel).classList.toggle(cls || "show")
}
