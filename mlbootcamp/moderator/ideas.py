def areas(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def area(box):
    return (box[:, 2] - box[:, 0]) * (box[:, 3] - box[:, 1])


def al(box):
    return box[:, 2] - box[:, 0]


def aw(box):
    return box[:, 3] - box[:, 1]


def als(box):
    return box[2] - box[0]


def aws(box):
    return box[3] - box[1]


def intersection_over_union(boxes):
    assert (len(boxes) == 8)
    boxA = boxes[:4].values
    boxB = boxes[4:].values

    boxAArea = areas(boxA)
    boxBArea = areas(boxB)

    if (boxAArea == 0 or boxBArea == 0):
        return 0

    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou