from utils.files import generate_absolute_path, read
from befree.api_model.cocreate.enums import WorkTags


class Utils:
    def set_collaboration_images(self, desktop="collab-desktop-png.png", mobile="collab-mobile-png.png"):
        images = {
            "images[desktop]": read(generate_absolute_path(f"befree/model/test_data/files/{desktop}")),
            "images[mobile]": read(generate_absolute_path(f"befree/model/test_data/files/{mobile}")),
        }

        return images

    def set_contest_images(self, desktop="contest-desktop-png.png", mobile="contest-mobile-png.png", main="contest-main-png.png"):
        files = {}
        if desktop is not None:
            files["images[desktop]"] = read(generate_absolute_path(f"befree/model/test_data/files/{desktop}"))
        if mobile is not None:
            files["images[mobile]"] = read(generate_absolute_path(f"befree/model/test_data/files/{mobile}"))
        if main is not None:
            files["images[main]"] = read(generate_absolute_path(f"befree/model/test_data/files/{main}"))

        return files

    def set_contest_rules(self, rules="rules.pdf"):
        files = {}
        if rules is not None:
            files["rules"] = read(generate_absolute_path(f"befree/model/test_data/files/{rules}"))

        return files

    def set_work_images(self, images=list(["collab-desktop-jpg.jpg"])):
        files = {}
        if images is not None:
            for i in range(0, len(images)):
                files[f"images[{i}]"] = read(generate_absolute_path(f"befree/model/test_data/files/{images[i]}"))

        return files

    def set_work_cover(self, cover="collab-desktop-jpg.jpg"):
        files = {}
        if cover is not None:
            files["cover"] = read(generate_absolute_path(f"befree/model/test_data/files/{cover}"))

        return files

    def set_work_tags(self, tags=list([WorkTags.Dizain.value, WorkTags.DigitalArt.value])):
        tags_list = {}
        if tags is not None:
            for i in range(0, len(tags)):
                tags_list[f"tags[{i}]"] = tags[i]

        return tags_list

    def set_avatar_image(self, avatar="avatar-png.png"):
        files = {}
        if avatar is not None:
            files["photo"] = read(generate_absolute_path(f"befree/model/test_data/files/{avatar}"))

        return files
