🔸 **Get upcoming fixtures**
```
!upcoming Premiership
```
![](https://i.imgur.com/gP9GP2K.png)

The little black box beside each fixture is the `id` of the fixture. This is how we identify it when making predictions. It's usually the same number +1 for each consecutive fixture.

🔸 **Make predictions**
```
!predict 569466:1-1 569467:3-9 569468:0-0 569469:4-0
```
![](https://i.imgur.com/thauolr.png)

You can set predictions as far in advance as you would like, and up to an hour before a game kicks off.

🔸 **View leaderboard**
```
!leaderboard Premiership
```
![](https://i.imgur.com/7Kah2E1.png)

You can also run `!leaderboard <league> table` to get the output in a tabular format.

🔸 **Make aliases**
```
!set_league_alias prem 2655
```
> You can find a league's `id` by running `!leagues`
> You can also use `!sla` as a shortcut, `!sta` for setting team aliases, etc.

Can't be arsed typing in 'Premiership' every time? You can alias things so you don't have to use their `id`. Now, for any command which requires a league you can use 'prem' (case-insensitive) instead of its `id`, e.g. `!fixtures prem`. This works for teams, fixtures, leagues, and users. It is global, so once you set an alias anyone can use it.

🔸 **Lots more**
That's the basics, but the bot does lots more.  Run `!help` or `!help <command>` to learn more. Read the full guide here: http://krd.me/bot/guide