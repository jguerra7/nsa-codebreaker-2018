# Task 3 - Connections
## Prompt
The Victim ID value identified in Task 1 is presumed to be unique per host. Depending on what information is used to generate the identifier and how it is computed, it may be possible to reverse the process and glean information about a victim from the identifier alone. This could help pinpoint infected hosts on a network and assist in remediation efforts. The goal of this task is to reverse-engineer how the unique Victim IDs are computed by the ransomware.


To prove your solution, compute the ID for a victim with information found in the victim_information.txt file attached below.

## Solution 
Once all of the task files are downloaded, decompile the binaries using `objdump -d`.
Our goal is to find out how the Victim IDs are being generated. Look through the function
names of both libraries for something that might be generated a unique ID. The most
obvious choice is the `cid` function in `libclient_crypt.so`.

At this point in the task, it's a good idea to use a disassembler like IDA or Cutter. It 
can be difficult to follow the structure of the program just looking at plain assembly. 
In the `cid` function, there are a few interesting calls to retrieve values like the OTP. 
One call we have not seen before is `HMAC`. 
```
1bf3:	e8 98 f0 ff ff       	callq  c90 <EVP_sha256@plt>
1bf8:	48 83 ec 08          	sub    $0x8,%rsp
1bfc:	4c 89 f1             	mov    %r14,%rcx
1bff:	41 b8 0a 00 00 00    	mov    $0xa,%r8d
1c05:	48 8d 54 24 0c       	lea    0xc(%rsp),%rdx
1c0a:	48 89 de             	mov    %rbx,%rsi
1c0d:	48 89 c7             	mov    %rax,%rdi
1c10:	52                   	push   %rdx
1c11:	44 89 fa             	mov    %r15d,%edx
1c14:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
1c19:	e8 82 f0 ff ff       	callq  ca0 <HMAC@plt>
```
Looking up this function, we can find documentation
that shows us that this is a keyed hash function for message authentication. The 
[documentation](https://www.openssl.org/docs/man1.0.2/crypto/hmac.html) for the function call
shows that the first argument takes the type of hash function being used. At address `1bf3` 
above, we can see that SHA256 is the hash function. 256 bits is 32 bytes, which translates
to 64 hex characters. Victim IDs are also 64 hex characters, hinting that we're on the right
track.

Let's see what the rest of the parameters for the call need. The second and third arguments
are the key and key length, the fourth and fifth arguments are the data and data length. If 
we can figure out what is being used for the key and data, then we can use that information
to construct our own HMAC call and get the Victim ID from the information provided. Using x86 
calling conventions, we can construct a table of the values and registers being passed to
the function:

Register| Argument  | Value
--------|-----------|-------
%rdi    |EVP_MD     |?  
%rsi    |key        |?
%rdx    |key length |?
%rcx    |data       |?
%r8     |data length|?
%r9     |output     |?
push    |output length|?

Now we need to go backwards and figure out where these values come from. Starting with the
first register, `%rdi`, it's value is copied over from `%rax`. This is the register that
functions place return values in, so this must be from the `EVP_sha256` call. Register `%r8`
is another easy one, it's value is the constant `0xa`. The key, key length, and data are a 
little trickier to find. The key can be traced back to a call to `base32_decode` that decodes
the OTP key. The data appears to have a starting address that matches where the return from a
function called `gia` is stored. Knowing this needs to be 10 bytes, we can look at where the
value is stored and take those bytes. Function names have been pretty insightful, so `gia` could
mean something like Get IP Address. IP addresses are 4 bytes, so that leaves 6 bytes to go. We
happen to know a 6 byte value: the OTP! Let's update our table with this new information: 

Register| Argument  | Value
--------|-----------|-------
%rdi    |EVP_MD     |EVP_sha256() 
%rsi    |key        |Base 32 decoded OTP key
%rdx    |key length |?
%rcx    |data       |IP address + OTP value
%r8     |data length|0xa (10)
%r9     |output     |?
push    |output length|?

With this info we should be able to create our own Victim IDs. I tried it on my own to make
sure it would work before trying it on the victim information provided. The `victim_id.sh` script
automates the solution for a given IP, OTP, and Key. First, the IP and OTP need to be converted
to hex, concatenated, and then converted to bytes. Second, the OTP key needs to be converted to
bytes. Finally, the `openssl` command can be used to generate the 256 bit hash:
```
echo -n "$DATA" | openssl sha256 -hmac $KEY
```
If this value matches with your Victim ID, try it using the victim information provided. My solution
was the following:
```
0xefba1a70d62d18bb333b02191df440d0b2c265879b31155f2d98e129fca4ac12
```
