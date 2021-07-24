import functools
import json
import logging
import os
import typing as T
from dataclasses import dataclass
from typing import Dict, List

from remarking import models
from remarking.highlight_extractor import highlight_extractor


@dataclass
class RawHighlight:
    """ Represent remarkable raw highlight entry"""
    start: int
    length: int
    text: str


def get_page_number_mapping(working_path: str, doc_id: str) -> T.Optional[Dict[str, int]]:
    """ Return a mapping of page id to page number or None if .content metadata file could not be found """
    contents_path = os.path.join(working_path, f"{doc_id}.content")
    if not os.path.exists(contents_path):
        logging.info(f"Could not find a contents file at {contents_path}")
        return None
    with open(contents_path, "r") as contents_file:
        page_ids = json.load(contents_file)["pages"]
    return {page_id: ind for ind, page_id in enumerate(page_ids)}


def create_raw_highlight(raw_highlight_data: Dict[str, T.Any]) -> RawHighlight:
    """ Create and return a raw highlight file given raw_highlight_data. """
    return RawHighlight(
        start=raw_highlight_data['start'],
        length=raw_highlight_data['length'],
        text=raw_highlight_data['text']
    )


def get_raw_highlights_by_page(working_path: str,
                               doc_id: str) -> T.Optional[Dict[str, List[RawHighlight]]]:
    """ Return raw highlights by page id for a given working_path that contains the passed document id. """
    raw_highlights: T.Dict[str, List[RawHighlight]] = {}

    highlights_path = os.path.join(working_path, f"{doc_id}.highlights")

    if not os.path.exists(highlights_path):
        logging.info(f"Could not find a highlights folder at {highlights_path}")
        return None

    highlights_files = os.listdir(highlights_path)
    for highlight_file in highlights_files:
        page_id = highlight_file.replace(".json", "")
        page_highlight_path = os.path.join(highlights_path, highlight_file)
        with open(page_highlight_path, "r") as highlights_file:
            highlights_by_layer: List[List[Dict[str, T.Any]]] = json.load(highlights_file)['highlights']
        raw_highlights_json: List[Dict[str, T.Any]] = functools.reduce(
            lambda l, r: l + r, highlights_by_layer, [])

        for raw_json in raw_highlights_json:
            raw_json['text'] = highlight_extractor.clean_highlight_text(raw_json['text'])

        raw_highlights[page_id] = [create_raw_highlight(raw_json) for raw_json in raw_highlights_json]
        raw_highlights[page_id] = sorted(raw_highlights[page_id], key=lambda x: x.start)
    return raw_highlights


class RemarkableHighlightExtractor(highlight_extractor.HighlightExtractor):
    """ Extracts highlights from the ``highlights`` folder of reMarkable documents. """

    @classmethod
    def get_extractor_instance_data(cls) -> List[highlight_extractor.ExtractorData]:
        return [
            highlight_extractor.ExtractorData(
                extractor_name="remarkable",
                instance=cls(),
                description=cls.__doc__
            )
        ]

    def get_highlights(self, working_path: str, document: models.Document) -> List[models.Highlight]:
        logging.info("Getting highlights from remarkable")
        extracted_highlight = []

        page_id_to_page_num = get_page_number_mapping(working_path, document.id)
        if page_id_to_page_num is None:
            logging.info(f"Failed to get page_id_to_page_num mapping for {document.id}")
            return []

        raw_highlights_by_page = get_raw_highlights_by_page(working_path, document.id)

        if raw_highlights_by_page is None:
            logging.info(f"Failed to get raw highlights for {document.id}")
            return []

        extracted_highlight.extend(
            self._from_raw_highlights(
                document.id, page_id_to_page_num, raw_highlights_by_page
            )
        )

        return extracted_highlight

    def _from_raw_highlights(self,
                             doc_id: str,
                             page_id_to_page_num: Dict[str, int],
                             raw_highlights_by_page: Dict[str, List[RawHighlight]]) -> List[models.Highlight]:
        """ Create Highlights from a list of RawHighlight """
        # TODO: This can join across pages most likely by checking lengths...
        # Need a way to know the length of a page in characters
        highlight_recs: T.List[models.Highlight] = []

        for page_id, page_raw_highlights in raw_highlights_by_page.items():

            highlight_text = page_raw_highlights[0].text if len(page_raw_highlights) > 1 else ""
            highlight_page = page_id_to_page_num[page_id]

            for i in range(1, len(page_raw_highlights)):
                prev_highlight = page_raw_highlights[i - 1]
                cur_highlight = page_raw_highlights[i]
                last_ending_index = prev_highlight.start + prev_highlight.length
                cur_ending_index = cur_highlight.start
                diff = cur_ending_index - last_ending_index
                if diff > 3:
                    # if our highlights distance is more than 3 character lets commit what we have
                    # as a highlight. Distance of 3 allows us to join across lines.
                    highlight_recs.append(
                        models.Highlight.create_highlight(
                            doc_id,
                            highlight_extractor.clean_highlight_text(highlight_text),
                            highlight_page,
                            self.__class__.__name__
                        )
                    )
                    highlight_text = page_raw_highlights[i].text
                    highlight_page = page_id_to_page_num[page_id]
                elif diff < 0:
                    # highlights overlap
                    highlight_text = (
                        highlight_text[:diff] +
                        cur_highlight.text +
                        (highlight_text[len(highlight_text) + diff + len(cur_highlight.text):]
                         if abs(diff) > len(cur_highlight.text) else ""
                        )
                    )
                else:  # diff == 0
                    # Highlights start and end at the same spot
                    highlight_text += " " + cur_highlight.text

            highlight_recs.append(
                models.Highlight.create_highlight(
                    doc_id,
                    highlight_extractor.clean_highlight_text(highlight_text),
                    highlight_page,
                    self.__class__.__name__
                )
            )
        return highlight_recs
