from docx.text.paragraph import Paragraph
from docx.image.image import Image
from docx.oxml.shape import CT_Picture
import docx
from docx.document import Document
from docx.parts.image import ImagePart

def get_picture(document: Document, paragraph: Paragraph):
    """
    document 为文档对象
    paragraph 为内嵌图片的段落对象
    """
    img = paragraph._element.xpath('.//pic:pic')
    if not img:
        return
    img: CT_Picture = img[0]
    embed = img.xpath('.//a:blip/@r:embed')[0]
    related_part: ImagePart = document.part.related_parts[embed]
    image: Image = related_part.image
    return image

def get_img_text(file_path, save_path):
    """
    获取word 图文信息
    :param file_path: 文件地址
    :return: word 文字 和图片信息字典
    """
    res_text = []
    res_img = []
    current_title = None
    d = docx.Document(file_path)
    for par in d.paragraphs:
        text_aim = par.text
        if text_aim is not None and text_aim != "":
            if par.style.font.size is not None and par.style.font.size >= docx.shared.Inches(0.2):
                current_title = text_aim
            res_text.append(text_aim)

        image = get_picture(d, par)
        if image is not None:
            # 二进制内容
            blob = image.blob
            # 写入 图片位置
            res_text.append("image")
            # 写入图片名称信息
            img_name = current_title if current_title else "image"
            res_img.append(save_path+"\\"+img_name+".png")

            # 生成图片
            w_img(blob, save_path+"\\"+img_name+".png")

    return {"text_arr": res_text, "img_arr": res_img}

def w_img(blob_data, save_path):
    """
    图片写入
    :param blob_data:
    :param save_path:
    :return:
    """
    with open(save_path, "wb") as f:
        f.write(blob_data)

file_path = "M9Z.docx"  # 你的 Word 文档地址
save_path = "extracted_images"  # 保存图片的文件夹路径
result = get_img_text(file_path, save_path)

# 输出结果
print("文字信息：")
for text in result["text_arr"]:
    print(text)

print("\n图片信息：")
for img_path in result["img_arr"]:
    print(img_path)