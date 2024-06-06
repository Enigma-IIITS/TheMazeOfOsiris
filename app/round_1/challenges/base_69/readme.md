# Base 69

## Introduction

Base 69 encoding and decoding is a method of converting binary data into a string composed of characters from a custom base 69 character set, and vice versa. This README provides a detailed explanation of the encoding and decoding processes, along with examples and code walkthroughs.

## Base 69 character set

Below is the custom character set for our base 69 encoding scheme

| 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   | 10  | 11  | 12  | 13  | 14  | 15  | 16  | 17  | 18  | 19  | 20  | 21  | 22  | 23  | 24  | 25  | 26  | 27  | 28  | 29  | 30  | 31  | 32  | 33  | 34  | 35  | 36  | 37  | 38  | 39  | 40  | 41  | 42  | 43  | 44  | 45  | 46  | 47  | 48  | 49  | 50  | 51  | 52  | 53  | 54  | 55  | 56  | 57  | 58  | 59  | 60  | 61  | 62  | 63  | 64  | 65  | 66  | 67  | 68  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 😀   | 😁   | 😂   | 😃   | 😄   | 😅   | 😆   | 😇   | 😈   | 😉   | 😊   | 😋   | 😌   | 😍   | 😎   | 😏   | 😐   | 😑   | 😒   | 😓   | 😔   | 😕   | 😖   | 😗   | 😘   | 😙   | 😚   | 😛   | 😜   | 😝   | 😞   | 😟   | 😠   | 😡   | 😢   | 😣   | 😤   | 😥   | 😦   | 😧   | 😨   | 😩   | 😪   | 😫   | 😬   | 😭   | 😮   | 😯   | 😰   | 😱   | 😲   | 😳   | 😴   | 😵   | 😶   | 😷   | 😸   | �   | 😺   | 😻   | 😼   | 😽   | 😾   | 😿   | 🙀   | 🙁   | 🙂   | 🙃   | 🙄   |

## Encoding to Base 69

Let's consider an example where we encode the string `Hello, World!` to base 69.

### Step 1: Convert String to ASCII Representation

Convert each character of the string to its ASCII representation:

```
ASCII Representation:
72 101 108 108 111 44 32 87 111 114 108 100 33
```

### Step 2: Convert ASCII to Binary Representation

Convert each ASCII value to its binary representation:

```
Binary Representation:
01001000 01100101 01101100 01101100 01101111 00101100 00100000 01010111 01101111 01110010 01101100 01100100 00100001
```

### Step 3: Combine Binary Representations

Combine the binary representations into a single binary value:

```
Combined Binary Value:
01001000011001010110110001101100011011110010110000100000010101110110111101110010011011000110010000100001
```

### Step 4: Convert Binary to Numerical Value

Interpret the combined binary value as a single numerical value:

```
Numerical Value:
5735816763073854918203775149089
```

### Step 5: Calculate Remainders

Continuously divide the numerical value by 69 and keep track of the remainders.

|     |                                 |     |
| --- | ------------------------------- | --- |
| 69  | 5735816763073854918203775149089 | 13  |
| 69  | 83127779174983404611648915204   | 41  |
| 69  | 1204750422825846443647085727    | 45  |
| 69  | 17460151055447049907928778      | 57  |
| 69  | 253045667470247100114909        | 27  |
| 69  | 3667328514061552175578          | 37  |
| 69  | 53149688609587712689            | 4   |
| 69  | 770285342167937865              | 27  |
| 69  | 11163555683593302               | 24  |
| 69  | 161790662081062                 | 25  |
| 69  | 2344792204073                   | 14  |
| 69  | 33982495711                     | 58  |
| 69  | 492499937                       | 17  |
| 69  | 7137680                         | 44  |
| 69  | 103444                          | 13  |
| 69  | 1499                            | 50  |
|     | 21                              | 21  |

### Step 6: Map Remainders to Base 69 Characters

Map each remainder to its corresponding character in the [base 69 character set](#base-69-character-set).

Base 69 Representation:

| 21  | 50  | 13  | 44  | 17  | 58  | 14  | 25  | 24  | 27  | 4   | 37  | 27  | 57  | 45  | 41  | 13  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 😕   | 😲   | 😍   | 😬   | 😑   | 😺   | 😎   | 😙   | 😘   | 😛   | 😄   | 😥   | 😛   | 😹   | 😭   | 😩   | 😍   |


## Encoding Strings to Base 69 in Python

```py
def decimal_to_radix(num: int) -> tuple[int]:
    num_in_radix = []  # List to store remainders
    while num != 0:
        # Get quotient and remainder when num is divided by 69
        num, remainder = divmod(num, 69)
        num_in_radix.append(remainder)  # Add the remainder to the list
    # Return the remainders in reverse order as a tuple, or (0,) if list is empty
    return tuple(num_in_radix[::-1]) if num_in_radix else (0,)

def encode(string: str) -> str:
    # Step 1: Convert string to its ASCII bytes representation
    string = string.encode("ascii")  # 'Hello, World!' -> 01001000011001010110110001101100011011110010110000100000010101110110111101110010011011000110010000100001 (b'Hello, World!')

    # Step 2: Combine the ASCII bytes into a single integer (big-endian)
    num = int.from_bytes(string, byteorder='big')  # b'Hello, World!' -> 5735816763073854918203775149089

    # Step 3: Convert the decimal integer to base 69
    num_in_radix = decimal_to_radix(num)  # 5735816763073854918203775149089 -> (21 , 50 , 13 , 44 , 17 , 58 , 14 , 25 , 24 , 27 , 4  , 37 , 27 , 57 , 45 , 41 , 13)

    # Step 4: Map the base 69 digits to corresponding characters in the custom set and return the value
    base_string = "😀😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏😐😑😒😓😔😕😖😗😘😙😚😛😜😝😞😟😠😡😢😣😤😥😦😧😨😩😪😫😬😭😮😯😰😱😲😳😴😵😶😷😸😹😺😻😼😽😾😿🙀🙁🙂🙃🙄"
    return "".join(base_string[i] for i in num_in_radix)  # (21 , 50 , 13 , 44 , 17 , 58 , 14 , 25 , 24 , 27 , 4  , 37 , 27 , 57 , 45 , 41 , 13) -> '😕😲😍😬😑😺😎😙😘😛😄😥😛😹😭😩😍'

# Example usage:
decoded_str = "Hello, World!"
encoded_str = encode(decoded_str)
print(encoded_str)  # Output: 😕😲😍😬😑😺😎😙😘😛😄😥😛😹😭😩😍

```

## Decoding from Base 69:

To decode the base 69 representation obtained by encoding `Hello, World!`

i.e., `😕😲😍😬😑😺😎😙😘😛😄😥😛😹😭😩😍`


### Step 1: Convert Base 69 Characters to Numerical Value

Map each base 69 character to its corresponding numerical value using the provided [base 69 character set](#base-69-character-set).

| 😕   | 😲   | 😍   | 😬   | 😑   | 😺   | 😎   | 😙   | 😘   | 😛   | 😄   | 😥   | 😛   | 😹   | 😭   | 😩   | 😍   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21  | 50  | 13  | 44  | 17  | 58  | 14  | 25  | 24  | 27  | 4   | 37  | 27  | 57  | 45  | 41  | 13  |

### Step 2: Calculate Numerical Value

Combine the numerical values obtained from each base 69 character to form a single numerical value by multiplying each value by the corresponding power of 69 and summing them up:

```
Numerical Value:
(21 * 69^16) + (50 * 69^15) + (13 * 69^14) + (44 * 69^13) + (17 * 69^12) + (58 * 69^11) + (14 * 69^10) + (25 * 69^9) + (24 * 69^8) + (27 * 69^7) + (4 * 69^6) + (37 * 69^5) + (27 * 69^4) + (57 * 69^3) + (45 * 69^2) + (41 * 69^1) + (13 * 69^0)
```

Evaluating this sum gives:

```
Numerical Value:
5735816763073854918203775149089
```

### Step 3: Convert Numerical Value to Binary Representation

Convert the numerical value obtained from step 2 to its binary representation.

|   |                                  |   |
| - | -------------------------------- | - |
| 2 | 5735816763073854918203775149089  | 1 |
| 2 | 2867908381536927459101887574544  | 0 |
| 2 | 1433954190768463729550943787272  | 0 |
| 2 | 716977095384231864775471893636   | 0 |
| 2 | 358488547692115932387735946818   | 0 |
| 2 | 179244273846057966193867973409   | 1 |
| 2 | 89622136923028983096933986704    | 0 |
| 2 | 44811068461514491548466993352    | 0 |
| 2 | 22405534230757245774233496676    | 0 |
| 2 | 11202767115378622887116748338    | 0 |
| 2 | 5601383557689311443558374169     | 1 |
| 2 | 2800691778844655721779187084     | 0 |
| 2 | 1400345889422327860889593542     | 0 |
| 2 | 700172944711163930444796771      | 1 |
| 2 | 350086472355581965222398385      | 1 |
| 2 | 175043236177790982611199192      | 0 |
| 2 | 87521618088895491305599596       | 0 |
| 2 | 43760809044447745652799798       | 0 |
| 2 | 21880404522223872826399899       | 1 |
| 2 | 10940202261111936413199949       | 1 |
| 2 | 5470101130555968206599974        | 0 |
| 2 | 2735050565277984103299987        | 1 |
| 2 | 1367525282638992051649993        | 1 |
| 2 | 683762641319496025824996         | 0 |
| 2 | 341881320659748012912498         | 0 |
| 2 | 170940660329874006456249         | 1 |
| 2 | 85470330164937003228124          | 0 |
| 2 | 42735165082468501614062          | 0 |
| 2 | 21367582541234250807031          | 1 |
| 2 | 10683791270617125403515          | 1 |
| 2 | 5341895635308562701757           | 1 |
| 2 | 2670947817654281350878           | 0 |
| 2 | 1335473908827140675439           | 1 |
| 2 | 667736954413570337719            | 1 |
| 2 | 333868477206785168859            | 1 |
| 2 | 166934238603392584429            | 1 |
| 2 | 83467119301696292214             | 0 |
| 2 | 41733559650848146107             | 1 |
| 2 | 20866779825424073053             | 1 |
| 2 | 10433389912712036526             | 0 |
| 2 | 5216694956356018263              | 1 |
| 2 | 2608347478178009131              | 1 |
| 2 | 1304173739089004565              | 1 |
| 2 | 652086869544502282               | 0 |
| 2 | 326043434772251141               | 1 |
| 2 | 163021717386125570               | 0 |
| 2 | 81510858693062785                | 1 |
| 2 | 40755429346531392                | 0 |
| 2 | 20377714673265696                | 0 |
| 2 | 10188857336632848                | 0 |
| 2 | 5094428668316424                 | 0 |
| 2 | 2547214334158212                 | 0 |
| 2 | 1273607167079106                 | 0 |
| 2 | 636803583539553                  | 1 |
| 2 | 318401791769776                  | 0 |
| 2 | 159200895884888                  | 0 |
| 2 | 79600447942444                   | 0 |
| 2 | 39800223971222                   | 0 |
| 2 | 19900111985611                   | 1 |
| 2 | 9950055992805                    | 1 |
| 2 | 4975027996402                    | 0 |
| 2 | 2487513998201                    | 1 |
| 2 | 1243756999100                    | 0 |
| 2 | 621878499550                     | 0 |
| 2 | 310939249775                     | 1 |
| 2 | 155469624887                     | 1 |
| 2 | 77734812443                      | 1 |
| 2 | 38867406221                      | 1 |
| 2 | 19433703110                      | 0 |
| 2 | 9716851555                       | 1 |
| 2 | 4858425777                       | 1 |
| 2 | 2429212888                       | 0 |
| 2 | 1214606444                       | 0 |
| 2 | 607303222                        | 0 |
| 2 | 303651611                        | 1 |
| 2 | 151825805                        | 1 |
| 2 | 75912902                         | 0 |
| 2 | 37956451                         | 1 |
| 2 | 18978225                         | 1 |
| 2 | 9489112                          | 0 |
| 2 | 4744556                          | 0 |
| 2 | 2372278                          | 0 |
| 2 | 1186139                          | 1 |
| 2 | 593069                           | 1 |
| 2 | 296534                           | 0 |
| 2 | 148267                           | 1 |
| 2 | 74133                            | 1 |
| 2 | 37066                            | 0 |
| 2 | 18533                            | 1 |
| 2 | 9266                             | 0 |
| 2 | 4633                             | 1 |
| 2 | 2316                             | 0 |
| 2 | 1158                             | 0 |
| 2 | 579                              | 1 |
| 2 | 289                              | 1 |
| 2 | 144                              | 0 |
| 2 | 72                               | 0 |
| 2 | 36                               | 0 |
| 2 | 18                               | 0 |
| 2 | 9                                | 1 |
| 2 | 4                                | 0 |
| 2 | 2                                | 0 |
| 2 | 1                                | 1 |
|   | 0                                | 0 | 

```
Binary Representation:
01001000011001010110110001101100011011110010110000100000010101110110111101110010011011000110010000100001
```

### Step 4: Split Binary Representation

Split the binary representation into chunks of 8 bits (1 byte) each.

```
Binary Chunks:
01001000 01100101 01101100 01101100 01101111 00101100 00100000 01010111 01101111 01110010 01101100 01100100 00100001
```

### Step 5: Convert Binary Representation to ASCII Values

Convert each binary chunk back to its corresponding ASCII value.

```
ASCII Values:
72 101 108 108 111 44 32 87 111 114 108 100 33
```

### Step 6: Construct Decoded String

Construct the decoded string by converting each ASCII value back to its corresponding character.

```
Decoded String:
Hello, World!
```

The decoded string is `Hello, World!`.

## Decoding Base 69 Encoded Strings in Python

```py
def radix_to_decimal(num_in_radix: tuple[int]) -> int:
    num = 0
    for digit in num_in_radix:
        num = num * 69 + digit  # Multiply the current number by 69 and add the current digit
    return num

def decode(encoded_string: str) -> str:
    # Custom base 69 character set
    base_string = "😀😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏😐😑😒😓😔😕😖😗😘😙😚😛😜😝😞😟😠😡😢😣😤😥😦😧😨😩😪😫😬😭😮😯😰😱😲😳😴😵😶😷😸😹😺😻😼😽😾😿🙀🙁🙂🙃🙄"

    # Step 1: Convert each character in the encoded string back to its base 69 digit
    num_in_radix = [base_string.index(c) for c in encoded_string] # 😕😲😍😬😑😺😎😙😘😛😄😥😛😹😭😩😍 -> (21 , 50 , 13 , 44 , 17 , 58 , 14 , 25 , 24 , 27 , 4  , 37 , 27 , 57 , 45 , 41 , 13)

    # Step 2: Convert the base 69 digits back to a decimal number
    num = radix_to_decimal(tuple(num_in_radix)) # (21 , 50 , 13 , 44 , 17 , 58 , 14 , 25 , 24 , 27 , 4  , 37 , 27 , 57 , 45 , 41 , 13) -> 5735816763073854918203775149089

    # Step 3: Calculate the number of bytes needed to represent the decimal number
    length = (num.bit_length() + 7) // 8

    # Step 4: Convert the decimal number back to bytes and then decode it to get the original string
    return num.to_bytes(length, byteorder='big').decode('ascii')

# Example usage:
encoded_str = "😕😲😍😬😑😺😎😙😘😛😄😥😛😹😭😩😍"
decoded_str = decode(encoded_str)
print(decoded_str)  # Output: Hello, World!
```
