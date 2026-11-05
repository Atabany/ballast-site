"""Prelaunch changes to pages that stay mostly the same as the live site.

Each entry is (exact text in _ops/content/<page>, replacement). The build stops if a text no longer
matches exactly once, so a change to the live copy can't leave the prelaunch page out of date
without anyone noticing. Whole-page rewrites live in _ops/prelaunch/pages/ instead.

Delete this file, _ops/prelaunch/ and the "prelaunch" block in discovery.json once 1.1.0 is live.
"""
UPDATED = ('"updated":"2026-11-04"', '"updated":"2026-11-05"')

EDITS = {
    'about.html': [UPDATED],

    'best-apps-to-quit-porn-compared.html': [
        UPDATED,
        ('New and unproven at scale. Free filter and urge flow, no account. No community.',
         'New and unproven at scale. Free urge flow, no account. No website filter in version 1.0.1. No community.'),
        ('''<li><strong>Accountability with another person's eyes on it.</strong> Ballast's trusted person holds a code; they don't get reports. If you want someone to be told, this isn't that.</li>''',
         '''<li><strong>Built-in blocking.</strong> Ballast 1.0.1 doesn't include a filter yet. Its friction checklist walks you through Apple's free Screen Time steps. If you want blocking inside the app, look at the apps above that have it.</li>
<li><strong>Accountability with another person's eyes on it.</strong> Ballast's partner card is something you choose to send yourself; nobody gets reports. If you want someone to be told, this isn't that.</li>'''),
        ('''<li><strong>The moment of need is free.</strong> The whole urge flow, slip support and the filter cost nothing, for good.''',
         '''<li><strong>The moment of need is free.</strong> The whole urge flow and slip support cost nothing, for good.'''),
        ('''There's no login to lose, and backup and restore are a file you keep.''',
         '''There's no login to lose, and you can export your main records to a file whenever you choose.'''),
        ('''<li><strong>A slip doesn't erase progress.</strong> Clear days accumulate and never reset.</li>''',
         '''<li><strong>A slip is treated as data.</strong> It restarts your current run, and your longest run and history stay. The next screen offers a few small things for the next hour, with no numbers on it.</li>'''),
        ('''<li><strong>Clean exit.</strong> If Pro ends, locks release and the filter stays under your control. A trusted-person lock always has a 24-hour way out.</li>
''', ''),
        ('''{{cta|If private and secular is what you're after.|Ballast's filter and urge flow are free, with no account. It has no community, and it is not treatment.}}''',
         '''{{cta|If private and secular is what you're after.|Ballast's urge flow is free, with no account. It has no community and no website filter yet, and it is not treatment.}}'''),
        ('''Ballast's urge flow, slip support and filter are free. Fortify''',
         '''Ballast's urge flow and slip support are free. Fortify'''),
    ],

    'block-porn-iphone-screen-time.html': [
        UPDATED,
        ('''what the filter misses, a seven-part setup checklist and where Ballast's own filter fits.''',
         '''what it misses, a seven-part setup checklist and where Ballast fits. Ballast 1.0.1 doesn't include a filter yet.'''),
        ('''<p>Below: the exact steps, how to lock them, the filter's limits, a seven-part checklist and where Ballast fits.''',
         '''<p>Below: the exact steps, how to lock them, what they miss, a seven-part checklist and where Ballast fits.'''),
        ('''Everything above is free and built into iOS, and it may be all you want. Ballast 1.1 adds a filter of its own and a plan for what the filter can't reach. It is one option, and I make it, so weigh this section accordingly.</p>
{{slot|ballast-shield-filter-and-commitment-lock-iphone|night|Ballast's Shield screen showing the adult-website filter turned on and the commitment lock settings.}}
<ul>
<li><strong>Filter (free).</strong> The <strong>Shield</strong> tab turns on Apple's adult-website filter with one tap, using Apple's Family Controls. Apple doesn't publish what counts as adult, so expect the same kind of misses and false matches as above. It also <a href="https://developer.apple.com/documentation/managedsettings/webcontentsettings/blockedbyfilter-swift.property">disables Safari private browsing</a>.</li>
<li><strong>Commitment lock (Pro).</strong> Instead of a Screen Time passcode, turning protection off needs a cool-off you chose in advance (10 minutes, 1 hour or 24 hours), or a code you sent once to someone you trust. If they can't be reached, a 24-hour wait always works.</li>
<li><strong>App shields (Pro).</strong> Choose apps in Apple's picker and shield them until a set time. The filter above doesn't cover what apps show in their own feeds; a shield is how you put a pause in front of those. The shield comes off the next time you open Ballast after that time.</li>
<li><strong>The urge flow (free).</strong> Tap what's happening, see your own if-then plan and your own reason, then choose to breathe, ride the wave or do the thing you planned. <a href="if-then-urge-plan.html">You can write a plan in your browser first</a>.</li>
<li><strong>Friction checklist (free).</strong> In the <strong>Plan</strong> tab's tools. It walks you through the seven jobs above with numbered steps.</li>
<li><strong>If it happens anyway.</strong> Log a slip and Ballast offers a few small things for the next hour. A slip is information you can plan with, your clear days stay counted and the setup you did stays in place. <a href="what-to-do-after-a-slip.html">More on the hours after a slip</a>.</li>
</ul>
<p class="note"><strong>The limit on all of this:</strong> a phone's owner can undo it in Settings. If you revoke Ballast's permission, the Shield screen tells you the shield is down. No App Store app can stop a determined owner. Ballast sells friction, not walls. If Pro ends, locks release cleanly and the filter stays under your control.</p>
<p>Your entries stay on your iPhone, no account is needed, and <a href="privacy.html">no browsing or app data leaves the phone</a>.</p>
{{cta|Set it up once, then have a plan for the hard minutes.|Ballast has a free filter and a free urge flow, on your iPhone, with no account.}}''',
         '''Everything above is free and built into iOS, and it may be all you want. <strong>Ballast 1.0.1 doesn't include a filter yet.</strong> It helps with the part a filter can't reach, the urge itself. It is one option, and I make it, so weigh this section accordingly.</p>
<ul>
<li><strong>The urge flow (free).</strong> Four steps: guided breathing, your own reasons, a timed urge-surfing exercise with your if-then plan beside it, then a short check-in. <a href="if-then-urge-plan.html">You can write a plan in your browser first</a>.</li>
<li><strong>Friction checklist (free).</strong> In the <strong>More</strong> tab. It walks you through the seven jobs above with numbered steps.</li>
<li><strong>If it happens anyway.</strong> Log a slip and Ballast offers a few small things for the next hour. A slip is information you can plan with, and the setup you did stays in place. <a href="what-to-do-after-a-slip.html">More on the hours after a slip</a>.</li>
</ul>
<p class="note"><strong>The limit on all of this:</strong> a phone's owner can undo Screen Time settings. No App Store app can stop a determined owner. These steps add friction, not walls.</p>
<p>Your entries stay on your iPhone and no account is needed. <a href="privacy.html">The privacy policy</a> has the details.</p>
{{cta|Set it up once, then have a plan for the hard minutes.|Ballast has a free urge flow, on your iPhone, with no account. It doesn't include a filter yet, so start with the steps above.}}'''),
        ('''<p>Yes, from version 1.1. One tap in the Shield tab turns on Apple's adult-website filter, for free. It is not a VPN and it has the same limits as any filter: it can miss sites, and a phone's owner can undo it in Settings. The free Screen Time steps above do a similar job with no app.</p>
<h3>Can Ballast stop me turning the filter off?</h3>
<p>Not absolutely. With Pro, turning protection off inside Ballast needs a cool-off you chose earlier or a code held by someone you trust, and a 24-hour wait always works if they can't be reached. A phone's owner can still undo it in Settings. It adds a pause, which is the point.</p>''',
         '''<p>Not in the current version. Ballast 1.0.1 doesn't include a filter yet. Its free friction checklist walks you through the Screen Time steps above, which need no app.</p>'''),
        ('''<p>The filter, the full urge flow, slip support and the friction checklist are free, with no account. Ballast Pro adds the commitment lock, app shields, unlimited urge plans, insights, the rest of the course and library, full history and a weekly review.</p>''',
         '''<p>The full urge flow, slip support and the friction checklist are free, with no account. Ballast Pro adds insights, the rest of the course and library, full history, extra habits and plans, and a weekly review.</p>'''),
        ('''and app steps describe Ballast 1.1; iOS menus''', '''and app steps describe Ballast 1.0.1; iOS menus'''),
    ],

    'how-to-stop-watching-porn.html': [
        UPDATED,
        ('''Ballast uses skills from CBT and ACT: your own if-then plans, a free urge flow and a filter, all on your iPhone with no account. It is not treatment.''',
         '''Ballast uses skills from CBT and ACT: your own if-then plans and a free urge flow, all on your iPhone with no account. It is not treatment.'''),
    ],

    'if-then-urge-plan.html': [
        UPDATED,
        ('''{{slot|ballast-plan-tab-my-urge-plans-iphone|dawn|Ballast's Urge plans screen, one tap from the Plan tab, showing the user's own card and a list of triggers to write cards for.}}
''', '''{{panel|dawn}}
'''),
        ('''Ballast shows your own if-then plan and reason the moment you tap what's happening. One plan and the whole urge flow are free. It is not treatment.''',
         '''Ballast's urge flow brings back your own reasons, then shows your if-then plan while you ride the urge out. One plan and the whole urge flow are free. It is not treatment.'''),
    ],

    'quittr-left-the-app-store.html': [
        ('''Ballast doesn't. Its setup simply asks how long since the last time, so you can carry your count across by hand;''',
         '''Ballast doesn't. Its setup simply asks when you last slipped, so you can carry your count across by hand;'''),
        ('''<strong>Can you get your data out and restore it?</strong> Lost streaks are a repeated complaint.''',
         '''<strong>Can you get your data out?</strong> Lost streaks are a repeated complaint.'''),
        ('''Ballast has no account and no server, and its filter and urge flow are free. It has no community, and it is not treatment.''',
         '''Ballast has no account and no server, and its urge flow is free. It has no community and no website filter yet, and it is not treatment.'''),
    ],

    'what-to-do-after-a-slip.html': [
        UPDATED,
        ('''If it sends you spiralling, try counting total clear days instead, which only ever goes up.</p>
{{slot|ballast-after-slip-next-hour-support-iphone|night|Ballast's after-slip screen, titled The next hour, offering a few small things to do.}}
<p>That's how Ballast is built. Log a slip and it offers a few small things for the next hour, and the day after, it reminds you the attempt is intact. <strong>Clear days never reset</strong>, your current run is shown second, and a slip appears on your route as an ordinary mark. You're never shown an offer at that moment. All of this is free.</p>''',
         '''If it sends you spiralling, try keeping a running total of good days instead, which only ever goes up.</p>
{{panel|night}}
<p>Here's how Ballast handles it today. Log a slip and it offers a few small things for the next hour, with no numbers on the screen, and the day after, it reminds you the attempt is intact. Your current run restarts, your longest run stays on the Today screen, and your history stays. You're never shown an offer at that moment. All of this is free.</p>'''),
        ('''Some people keep a run counter; others find total clear days more honest and easier to live with.''',
         '''Some people keep a run counter; others find a running total more honest and easier to live with.'''),
    ],
}
