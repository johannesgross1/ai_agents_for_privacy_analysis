import base64
import urllib.parse


def __replace_base64_mp(content):
    if content is not None and content.startswith('data=W') or content.startswith('data=e'):
        try:
            b64 = content[content.index('='):content.index('%')] + '=='
        except ValueError:
            b64 = content[content.index('='):] + '=='
        try:
            if len(b64) % 3 != 0:
                b64 += '=' * (3 - len(b64) % 3)
            dec = base64.b64decode(b64, '-_')
            return 'data=' + dec.decode('utf-8')
        except Exception as e:
            return 'data=BASE64_ERROR ' + str(e) + content[-10:]
    else:
        return content


def __replace_base64_clue(content):
    if content is not None and content.startswith('{"schema":"iglu:com') or content.startswith('{"p":"ey'):
        try:
            start_block_1 = content.index('eyJ')
            end_block_1 = content.index('"', start_block_1)
            start_block_2 = content.index('eyJ', end_block_1)
            end_block_2 = content.index('"', start_block_2)
        except ValueError:
            start_block_1 = -1
            end_block_1 = -1
            start_block_2 = -1
            end_block_2 = -1

        try:
            if start_block_1 < 0:
                return content

            block_1 = content[start_block_1:end_block_1]
            block_1_decoded = base64.b64decode(block_1, '-_').decode('utf-8')

            if start_block_2 > 0:
                block_2 = content[start_block_2:end_block_2]
                block_2_decoded = base64.b64decode(block_2, '-_').decode('utf-8')

                content = (content[:start_block_1] + block_1_decoded
                           + content[end_block_1:start_block_2] + block_2_decoded + content[end_block_2:])
            else:
                content = content[:start_block_1] + block_1_decoded + content[end_block_1:]
        except Exception as e:
            content = (content[:start_block_1] + 'BASE64_ERROR: ' + str(e)
                       + content[end_block_1:start_block_2] + 'BASE64_ERROR: ' + str(e) + content[end_block_2:])

        return content
    else:
        return content


def __replace_binary_data(cell):
    try:
        # Try decoding as utf-8
        cell.decode('utf-8')
        # If successful, return the cell as is
        return cell
    except AttributeError:
        # This exception is raised if the object is already a str, indicating it's not binary
        return cell
    except Exception:
        # If any other exception is raised, replace the content with "BINARY_DATA"
        return "BINARY_DATA"


def __clean_base64(traffic):
    traffic['request_content'] = traffic.apply(
        lambda row: __replace_base64_mp(row['request_content'])
        if row['request_content'] is not None and row['request_content_length'] > 0 else row['request_content'], axis=1)

    traffic['request_content'] = traffic.apply(
        lambda row: __replace_base64_clue(row['request_content'])
        if row['request_content'] is not None and row['request_content_length'] > 0 else row['request_content'], axis=1)


def __clean_urlencoded(traffic):
    traffic['request_content'] = traffic.apply(
        lambda row: urllib.parse.unquote(row['request_content'])
        if row['request_content'] is not None and row['request_content_length'] > 0 else row['request_content'], axis=1)


def __clean_binary(traffic):
    # identify binary data in request_content and response_content and replace it with a placeholder
    # only replace if the content is not empty
    traffic['request_content'] = traffic.apply(
        lambda row: __replace_binary_data(row['request_content'])
        if row['request_content'] is not None and row['request_content_length'] > 0 else row['request_content'], axis=1)


def __clean_response(traffic):
    traffic['response_content'] = traffic.apply(
        lambda row: None
        if row['response_content_length'] > 0 else row['response_content'], axis=1)


def clean_traffic(traffic):
    traffic_copy = traffic.copy()
    __clean_response(traffic_copy)
    __clean_base64(traffic_copy)
    __clean_binary(traffic_copy)
    __clean_urlencoded(traffic_copy)
    return traffic_copy
