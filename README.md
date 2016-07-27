# slackmover

A tiny silly script to...

* retrieve and archive messages as json file (works for both public/private channels)
* copy messages from private to public channel in a quite-dumb way


## Requirements
* Python 3.5.1
  * because this uses type hinting (certainly not necessary, just out of curiosity)
* pip installable packages
  * slackclient
  * click (cli parser)

## Usage
You'll need Slack API token.

```sh
# --help to show CUI help
./slackmover.py --help
```

```sh
# subcommand: archive
# example: retrieve messages in "dev" channel and save as json file
./slackmover.py archive dev --token $(cat slacktoken.txt)
```

```sh
# subcommand: mirror
# example: copy messages in private channel to public channel
#          this will just post messages with additional time-stamp messages
./slackmover.py mirror __dev__ dev --token $(cat slacktoken.txt)

```

### Result (mirror)
src: private channel (`__dev__`)
![](img/mirror-from.png)

dest: public channel (`dev`)
![](img/mirror-to.png)
