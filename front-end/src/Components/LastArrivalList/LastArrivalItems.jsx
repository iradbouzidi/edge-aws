import React from 'react';
import styled from 'styled-components'

const LastArrivalItems = props => {
    // * ---------- STYLES ---------- *
    const OneResult = styled.div`
        //background: #282c34;
        //color: #fff;
        padding: 15px;
        //border-radius: 6px;
        margin: 30px 0;
        min-width: 80%;
        -moz-box-shadow:    3px 3px 8px 3px #ccc;
        -webkit-box-shadow: 3px 3px 8px 3px #ccc;
        box-shadow:         3px 3px 8px 3px #ccc;
`
    const ListItem = styled.li`
        list-style: none;
        margin-bottom: 5px;
`
    const UlList = styled.ul`
      min-width: 100%;
`

    return (
            <OneResult>
                <UlList>
                    <ListItem><b>Name:</b> <i>{ props.result[1] } </i></ListItem>
                    <ListItem><b>Date:</b> <i>{ props.result[2] } </i></ListItem>
                    <ListItem><b>Arrival Time:</b> <i>{ props.result[3] } </i></ListItem>
                    <ListItem><b>Departure Time:</b> <i>{ props.result[4] } </i></ListItem>
                    <ListItem><b>Arrival Picture Path:</b> <i>{ props.result[5] } </i></ListItem>
                    <ListItem><b>Departure Picture Path:</b> <i>{ props.result[6] } </i></ListItem>
                </UlList>
            </OneResult>
    );
};

export default LastArrivalItems;
