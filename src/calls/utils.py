def decode_icecandidate(data: dict) -> dict:
    result = dict()
    """
    component: int
    foundation: str
    ip: str
    port: int
    priority: int
    protocol: str
    type: str
    relatedAddress: Optional[str] = None
    relatedPort: Optional[int] = None
    sdpMid: Optional[str] = None
    sdpMLineIndex: Optional[int] = None
    tcpType: Optional[str] = None
    """
    if len(data['candidate']) > 0:
        candidate = data['candidate'].split()

        result['foundation'] = candidate[0].split(':')[1]
        result['component'] = 'rtp' if candidate[1] == '1' else 'rtcp'
        result['protocol'] = candidate[2]
        result['priority'] = candidate[3]
        result['ip'] = candidate[4]
        result['port'] = candidate[5]
        result['type'] = candidate[7]
        if len(candidate) > 8:
            result['tcptype'] = candidate[9]
        result['sdpMid'] = data['sdpMid']
        result['sdpMLineIndex'] = data['sdpMLineIndex']
    return result


if __name__ == '__main__':
    example = {'candidate': 'candidate:0 1 UDP 2122252543 192.168.79.73 51536 typ host',
               'sdpMid': '0', 'sdpMLineIndex': 0,
               'usernameFragment': 'c64f570b'}

    print(decode_icecandidate(example))
