#!/bin/bash
ip xfrm state flush
ip xfrm policy flush

#SAD
ip xfrm state add src 10.0.1.1 dst 10.0.1.2 proto esp spi 0x10001 mode transport enc 'cbc(aes)' 0x0123456789abcdef0123456789abcdef
ip xfrm state add src 10.0.1.2 dst 10.0.1.1 proto esp spi 0x10002 mode transport enc 'cbc(aes)' 0xabcdef0123456789abcdef0123456789

#SPD (ESP in Transport Mode)
ip xfrm policy add src 10.0.1.2 dst 10.0.1.1 dir out tmpl proto esp mode transport
ip xfrm policy add src 10.0.1.2 dst 10.0.1.1 dir in tmpl proto esp mode transport
ip xfrm policy add src 10.0.1.1 dst 10.0.1.2 dir out tmpl proto esp mode transport
ip xfrm policy add src 10.0.1.1 dst 10.0.1.2 dir in tmpl proto esp mode transport
