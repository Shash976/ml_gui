from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


path = r"C:\Users\shashg\Downloads\the-man-in-the-high-castle-season-3-729x486-1540221492.jpg"

img = Image.open(path)

def get_count(img):
    total_r=total_g=total_b=black_pixels=black_r=black_g=black_b=0
    [xs,ys] = img.size
    total_pixels = xs*ys
    img = np.array(img)
    for x in range(xs):
        for y in range(ys):
            [r,g,b] = img[y][x][0:3]
            if (r+g+b) <= 40:
                black_pixels+=1
                black_r+=r
                black_b+=b
                black_g+=g
                img[y][x] = [0,255,0]
            total_r+=r
            total_b+=b
            total_g+=g
    avg_r= total_r/ total_pixels
    avg_g =total_g/ total_pixels
    avg_b = total_b/ total_pixels
    avg_black_r= (total_r-black_r)/(total_pixels-black_pixels)
    avg_black_g= (total_g-black_g)/(total_pixels-black_pixels)
    avg_black_b= (total_b-black_b)/(total_pixels-black_pixels)
    return img, avg_r, avg_b, avg_g, avg_black_r,avg_black_g, avg_black_b

image, r,g,b,br,bg,bb=get_count(img)

print(r, g,b, br,bg,bb)

plt.imshow(image)
plt.show()