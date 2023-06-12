import os
import json
import requests
from PIL import Image
from github import Github


def get_image():
    response = requests.get(
        "https://sugoiapi.hayasaka.moe/v1/art/random?orien=portrait"
    )

    img_link = json.loads(response.text)["url"]

    img_data = requests.get(img_link).content

    with open(img_link.split("/")[-1], "wb") as handler:
        handler.write(img_data)

    return img_link.split("/")[-1]


def crop_image(image_name):
    img = Image.open(image_name)

    img = img.resize((int(img.width * (1000 / img.height)), 1000))
    img = img.crop(((img.width / 2) - 250, 0, (img.width / 2) + 250, 1000))

    img.save(image_name)

    upload_image(image_name)


def upload_image(image_name):
    token = os.getenv("GH_TOKEN")

    repo = Github(token).get_repo("anna-anarchy/anna-anarchy")

    repo.create_file(
        f"images/{image_name}",
        f"Add {image_name}",
        open(image_name, "rb").read(),
    )

    for file in repo.get_contents("images"):
        if file.name != image_name:
            repo.delete_file(file.path, "Remove old images", file.sha)

    os.remove(image_name)

    update_readme(image_name)


def update_readme(image_name):
    token = os.getenv("GH_TOKEN")

    repo = Github(token).get_repo("anna-anarchy/anna-anarchy")

    readme = repo.get_contents("README.md")

    repo.update_file(
        "README.md",
        "Update README.md",
        '<p float="left"> <img src="images/'
        + image_name
        + '" width="250" align="left"> <p float="left"> <samp> anna <br>i like making things <br><br>languages: <a href="https://www.rust-lang.org/">rust</a>, <a href="https://www.lua.org/">lua</a>, <a href="https://www.python.org/">python</a> <br><br><a href="https://jackli.dev/discord">tumblr</a> <br><br>yoinked from <a href="https://github.com/jckli">/jckli</a> </samp> </p></p>',
        readme.sha,
        branch="main",
    )


def main():
    crop_image(get_image())


if __name__ == "__main__":
    main()