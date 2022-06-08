#!/usr/bin/env python3
# https://github.com/MrBlaise/learnpython/blob/master/Numbers/pi.py
# Find PI to the Nth Digit

def generator(significant_digits):

    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3

    decimal = int(significant_digits)
    counter = 0

    while counter != decimal + 1:
        if 4 * q + r - t < n * t:
            # yield digit
            yield n
            # insert period after first digit
            if counter == 0:
                yield '.'
            # end
            if decimal == counter:
                print('')
                break
            counter += 1
            nr = 10 * (r - n * t)
            n = ((10 * (3 * q + r)) // t) - 10 * n
            q *= 10
            r = nr
        else:
            nr = (2 * q + r) * l
            nn = (q * (7 * k) + 2 + (r * l)) // (t * l)
            q *= k
            t *= l
            l += 2
            k += 1
            n = nn
            r = nr


def main(cache, significant_digits):
    """
    calculate PI
    """
    pi_digits = generator(significant_digits)
    i = 0
    ret_value = ''

    for d in pi_digits:
        ret_value += str(d)
        print(d, end='')
        i += 1
        if i == 40:
            print("")
            i = 0

    return ret_value


def console_main():
    digits = int(input("Enter the number of decimals to calculate to: "))
    main(0, digits)


if __name__ == '__main__':
    console_main()
    # main(0, 4)
