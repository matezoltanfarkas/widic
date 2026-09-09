# widic
A Wiktionary viewer in your Terminal. From Multilinguals to Multilinguals.

Officially tested languages are English (en), German (de) and French (fr). Implemented languages are (these need some verification!):
* Spanish (es)

Other languages might have some rendering quirks due to differing Wiktionary styles.
However, `widic` is Wiktionary-site agnostic and freely extensible! Just make sure to use the correct language code (the `XX` part in `XX.wiktionary.org`)

Still in development. Please leave a bug report for feedback and wishes!

# How it works
`widic` fetches the desired Wiktionary site, strips of its tables and figures and converts the remaining content into Markdown, which is then displayed in your terminal.

For this reason, internet connection is required.

# Demo:
![demo](demo.gif)
