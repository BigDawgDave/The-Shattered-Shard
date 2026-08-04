# The Shattered Sigil
## Player Guide

The Aegis Sigil protected the wizard's tower until an unknown adversary broke it
into ten runes. You are the newest apprentice. Recover each rune and restore the
ward before the Lich reaches the archive.

This guide explains how to participate without revealing solutions.

## What you need

- The badge and a charged battery
- A laptop or phone with Wi-Fi and a web browser
- A data-capable USB cable
- A serial terminal for one chapter
- A small jumper wire for one physical chapter
- Optional tools such as browser developer tools, `curl`, a port scanner,
  CyberChef, or a short script

Use only the badge assigned to you and the services it advertises. Do not test
conference infrastructure or other attendees' devices.

## Starting the quest

1. Turn on the badge.
2. Join its network:

   ```text
   Arcane-Sigil-XXXXXX
   ```

3. Use password:

   ```text
   spellbook
   ```

4. If the portal does not open automatically, browse to:

   ```text
   http://192.168.4.1
   ```

5. Open **Quest Log**. Chapters unlock in order.

## Setting your handle

Open **Handle** in the portal navigation and enter up to 24 characters. Letters,
numbers, `_`, `-`, `.`, `!`, `@`, and `#` are supported. Once saved, the badge
scrolls only your handle. Submitting an empty handle returns the panel to
SSID-only mode.

Without a handle, the SSID scrolls red while no device is connected and green
when at least one device is connected to the AP.

## Changing the Wi-Fi password

The initial password is `spellbook`. After joining, open **Network**, enter a new
password twice, and select **Save and restart**. The password must contain 8-63
printable characters. The badge disconnects clients, reboots, and keeps the same
SSID. Rejoin it using the new password.

## Rune submission and progress

Most chapters reveal a flag in this format:

```text
RUNE{NN-XXXXXXXX}
```

Submit it through **Submit Rune**. Flags are generated uniquely for each badge,
so another player's flag will not work on yours.

Chapters 7 and 8 validate directly on the badge. When either physical action is
correct, the corresponding progress region illuminates automatically.

The **Status** page displays the fragment earned for every restored chapter.
Record those fragments. They are required for the finale.

When a handle is configured, its scrolling color changes through eleven clearly
separated colors as progress increases: red at the beginning, then warm colors,
green, cyan, blue, indigo, and violet after all ten chapters are complete.

## Safe hardware interaction

- Power the badge off before connecting or removing a jumper.
- For the familiar challenge, connect only the labeled SAO `GPIO1` and `GPIO2`.
- Never bridge power to ground.
- Never apply external voltage to an SAO or ESP32 pin.
- Do not remove components, short random pads, or connect a programmer unless an
  organizer explicitly authorizes it.

## Serial access

Use the CP2102 programming connector and open the COM port at:

```text
115200 baud, 8 data bits, no parity, 1 stop bit
```

In PlatformIO:

```powershell
pio device monitor --baud 115200
```

Enter `help` to see the permitted commands.

## Progressive hints

### Chapter 1 - The Wizard's Knock

1. Start as a polite automated visitor would.
2. Web crawlers are commonly given a small text file containing instructions.
3. Inspect `/robots.txt`.

### Chapter 2 - Runes on the Gate

1. A page is more than the words visible in the browser.
2. Inspect the resources that control its appearance.
3. Decode the marginal note in the stylesheet.

### Chapter 3 - The Mimic's Form

1. The mimic trusts appearances.
2. Inspect the complete form submission, including hidden fields.
3. Present a more powerful role than `guest`.

### Chapter 4 - Goblin Quartermaster

1. Test the assumptions behind the quantity field.
2. Buying and returning are arithmetically related.
3. Consider what a negative purchase does to the goblin's gold calculation.

### Chapter 5 - Scrying Pool

1. The badge may listen on more than one TCP port.
2. Enumerate only `192.168.4.1`.
3. The second service explains which HTTP header opens true sight.

### Chapter 6 - Whispers in the Wand

1. Connect through the CP2102 UART.
2. Enter `help`.
3. The chapter prompt tells you what the wand wants whispered.

### Chapter 7 - The Runic Lantern 

1. Awaken the lantern and watch the LED panel rather than the web page. 
2. Record the four groups of binary digits displayed on the panel. Each group contains four digits.
3. Convert each four-bit binary group into one hexadecimal digit. 
4. Enter the resulting four-digit hexadecimal code in the portal. 
5. Preserve leading zeroes. If needed, replay the lantern to observe the sequence again.

### Chapter 8 - Familiar on the Wire

1. Turn off the badge before adding the jumper.
2. Bridge only SAO GPIO1 and GPIO2.
3. Restart, open the chapter, and wake the familiar.

### Chapter 9 - The Crystal Archive

1. Download the archive and read it as text first.
2. The file identifies its cipher and key.
3. Decode the hexadecimal data and apply the named repeating-key operation.

### Chapter 10 - The Lich's Cipher

1. Review the nine fragments shown on the Status page.
2. Preserve chapter order.
3. Read the first glyph of each fragment as one incantation.

## Recovery

If the interface stops responding:

1. Disconnect from the badge network.
2. Power-cycle the badge.
3. Rejoin the same SSID.
4. Browse directly to `http://192.168.4.1`.

Progress survives normal power cycles. To intentionally restart the campaign,
open the serial console and enter `reset-progress`.
